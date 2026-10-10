"""NURVEX node prototype v0.3 — experimental peer sync, NOT production-ready."""
from __future__ import annotations
import argparse, hashlib, json, os, sys, time, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
    from cryptography.hazmat.primitives import serialization
except ImportError:
    print("Missing dependency. Run: python -m pip install -r requirements.txt", file=sys.stderr)
    raise

ROOT = Path(__file__).resolve().parent
DATA = Path(os.environ.get("NURVEX_DATA_DIR", str(ROOT / "data"))).expanduser().resolve()
CHAIN_FILE = DATA / "chain.json"
MEMPOOL_FILE = DATA / "mempool.json"
PEERS_FILE = DATA / "peers.json"
COIN = 100_000_000
MAX_SUPPLY = 18_000_000 * COIN
INITIAL_REWARD = 857_142_857  # 8.57142857 NVRX
HALVING_INTERVAL = 1_050_000
POW_PREFIX = "00000"  # prototype difficulty; NOT suitable for a public network
PROTOCOL = "NURVEX-TESTNET-0.3"
MAX_FUTURE_DRIFT = 2 * 60 * 60
MAX_PAST_DRIFT = 2 * 60 * 60


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def address_for(public_key_hex: str) -> str:
    return "nvrx1" + sha256(bytes.fromhex(public_key_hex))[:40]


def reward_for_height(height: int) -> int:
    return INITIAL_REWARD >> (height // HALVING_INTERVAL)


def amount_to_units(value: str) -> int:
    from decimal import Decimal, InvalidOperation
    try:
        amount = Decimal(value)
    except InvalidOperation as e:
        raise ValueError("Invalid amount") from e
    units = amount * COIN
    if amount <= 0 or units != units.to_integral_value():
        raise ValueError("Amount must be positive and have at most 8 decimal places")
    return int(units)


def fmt(units: int) -> str:
    return f"{units / COIN:.8f}".rstrip("0").rstrip(".") or "0"


def signable_tx(tx: dict) -> dict:
    return {k: v for k, v in tx.items() if k != "signature"}


def tx_id(tx: dict) -> str:
    return sha256(canonical(tx))


def verify_tx(tx: dict) -> bool:
    try:
        if tx.get("type") != "transfer": return False
        if not isinstance(tx.get("amount"), int) or tx["amount"] <= 0: return False
        if not isinstance(tx.get("nonce"), int) or tx["nonce"] < 1: return False
        pub_hex = tx["public_key"]
        if address_for(pub_hex) != tx["sender"]: return False
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub_hex)).verify(bytes.fromhex(tx["signature"]), canonical(signable_tx(tx)))
        return True
    except Exception:
        return False


def fresh_chain() -> list[dict]:
    genesis = {"height": 0, "timestamp": 0, "previous_hash": "0" * 64, "transactions": [], "nonce": 0, "protocol": PROTOCOL}
    genesis["hash"] = sha256(canonical(genesis))
    return [genesis]


TARGET_BLOCK_TIME = 60
DIFFICULTY_ADJUST_INTERVAL = 10
MIN_DIFFICULTY = 5
MAX_DIFFICULTY = 8
GENESIS_DIFFICULTY = 5


def current_difficulty(chain: list[dict]) -> int:
    height = len(chain)
    if height < DIFFICULTY_ADJUST_INTERVAL:
        return GENESIS_DIFFICULTY
    last = (height // DIFFICULTY_ADJUST_INTERVAL) * DIFFICULTY_ADJUST_INTERVAL
    prev = last - DIFFICULTY_ADJUST_INTERVAL
    if prev < 0 or last >= len(chain):
        return GENESIS_DIFFICULTY
    span = chain[last]["timestamp"] - chain[prev]["timestamp"]
    target = TARGET_BLOCK_TIME * DIFFICULTY_ADJUST_INTERVAL
    zeros = GENESIS_DIFFICULTY + (height // DIFFICULTY_ADJUST_INTERVAL - 1)
    zeros = max(MIN_DIFFICULTY, min(zeros, MAX_DIFFICULTY))
    if span < target // 2:
        return min(zeros + 1, MAX_DIFFICULTY)
    if span > target * 2:
        return max(zeros - 1, MIN_DIFFICULTY)
    return zeros


def required_prefix(chain: list[dict]) -> str:
    return "0" * current_difficulty(chain)


def is_timestamp_valid(block: dict, reference_time=None) -> tuple:
    ref = reference_time if reference_time is not None else int(time.time())
    ts = block.get("timestamp")
    if not isinstance(ts, int):
        return False, "timestamp is not an integer"
    if ts == 0:
        return True, "genesis"
    if ts > ref + MAX_FUTURE_DRIFT:
        return False, "timestamp too far in future"
    if ts < ref - MAX_PAST_DRIFT:
        return False, "timestamp too far in past"
    return True, "ok"

def block_hash(block: dict) -> str:
    return sha256(canonical({k: v for k, v in block.items() if k != "hash"}))


def load_json(path: Path, default: Any) -> Any:
    if not path.exists(): return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, value: Any) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def load_chain() -> list[dict]:
    return load_json(CHAIN_FILE, fresh_chain())


def save_chain(chain: list[dict]) -> None:
    save_json(CHAIN_FILE, chain)


def balances_and_nonces(chain: list[dict]) -> tuple[dict[str, int], dict[str, int], int]:
    balances: dict[str, int] = {}
    nonces: dict[str, int] = {}
    issued = 0
    for block in chain[1:]:
        for tx in block["transactions"]:
            if tx["type"] == "coinbase":
                balances[tx["recipient"]] = balances.get(tx["recipient"], 0) + tx["amount"]
                issued += tx["amount"]
            else:
                balances[tx["sender"]] = balances.get(tx["sender"], 0) - tx["amount"]
                balances[tx["recipient"]] = balances.get(tx["recipient"], 0) + tx["amount"]
                nonces[tx["sender"]] = tx["nonce"]
    return balances, nonces, issued


def validate_chain(chain: list[dict]) -> tuple[bool, str]:
    if not chain: return False, "Empty chain"
    if chain[0] != fresh_chain()[0]: return False, "Unexpected genesis block"
    balances: dict[str, int] = {}
    nonces: dict[str, int] = {}
    issued = 0
    for idx, block in enumerate(chain[1:], start=1):
        if block.get("height") != idx: return False, f"Wrong height at block {idx}"
        if block.get("previous_hash") != chain[idx-1].get("hash"): return False, f"Broken link at block {idx}"
        ts_ok, ts_why = is_timestamp_valid(block, reference_time=chain[idx-1].get("timestamp") or int(time.time()))
        if not ts_ok: return False, f"Invalid timestamp at block {idx}: {ts_why}"
        if block_hash(block) != block.get("hash"): return False, f"Invalid hash at block {idx}"
        expected_prefix = "0" * GENESIS_DIFFICULTY if idx < DIFFICULTY_ADJUST_INTERVAL else required_prefix(chain[:idx])
        if not block["hash"].startswith(expected_prefix): return False, f"Insufficient proof of work at block {idx} (expected {len(expected_prefix)} zeros)"
        txs = block.get("transactions", [])
        if not txs or txs[0].get("type") != "coinbase" or len([t for t in txs if t.get("type") == "coinbase"]) != 1:
            return False, f"Invalid coinbase at block {idx}"
        expected_reward = min(reward_for_height(idx), MAX_SUPPLY - issued)
        coinbase = txs[0]
        if coinbase.get("amount") != expected_reward or expected_reward <= 0:
            return False, f"Invalid mining subsidy at block {idx}"
        if not isinstance(coinbase.get("recipient"), str) or not coinbase["recipient"].startswith("nvrx1"):
            return False, f"Invalid miner address at block {idx}"
        for tx in txs[1:]:
            if not verify_tx(tx): return False, f"Invalid signature/transaction in block {idx}"
            sender, recipient = tx["sender"], tx["recipient"]
            if not isinstance(recipient, str) or not recipient.startswith("nvrx1"): return False, "Invalid recipient address"
            expected_nonce = nonces.get(sender, 0) + 1
            if tx["nonce"] != expected_nonce: return False, f"Invalid nonce for {sender}"
            if balances.get(sender, 0) < tx["amount"]: return False, f"Insufficient balance for {sender}"
            balances[sender] -= tx["amount"]
            balances[recipient] = balances.get(recipient, 0) + tx["amount"]
            nonces[sender] = tx["nonce"]
        balances[coinbase["recipient"]] = balances.get(coinbase["recipient"], 0) + coinbase["amount"]
        issued += coinbase["amount"]
        if issued > MAX_SUPPLY: return False, "Maximum supply exceeded"
    return True, "OK"


def init() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    if CHAIN_FILE.exists(): print(f"Chain already exists: {CHAIN_FILE}")
    else:
        save_chain(fresh_chain())
        print(f"Initialized NURVEX local test chain: {CHAIN_FILE}")
    if not MEMPOOL_FILE.exists(): save_json(MEMPOOL_FILE, [])
    print("This is a single-node prototype, not a public network or real money system.")


def new_wallet(path_str: str) -> None:
    path = Path(path_str).expanduser().resolve()
    if path.exists(): raise ValueError(f"Refusing to overwrite existing wallet: {path}")
    private = Ed25519PrivateKey.generate()
    priv_raw = private.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())
    pub_raw = private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    wallet = {"network": PROTOCOL, "private_key_hex": priv_raw.hex(), "public_key_hex": pub_raw.hex(), "address": address_for(pub_raw.hex()), "warning": "Keep this file secret. Prototype only; do not store real funds."}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(wallet, indent=2), encoding="utf-8")
    try: os.chmod(path, 0o600)
    except OSError: pass
    print(f"Wallet created: {path}\nAddress: {wallet['address']}\nKeep the wallet file private and backed up.")


def wallet_read(path_str: str) -> dict:
    wallet = json.loads(Path(path_str).expanduser().read_text(encoding="utf-8"))
    if wallet.get("network") != PROTOCOL: raise ValueError("Wallet belongs to another network/protocol")
    return wallet


def balance_cmd(address: str) -> None:
    chain = load_chain(); ok, why = validate_chain(chain)
    if not ok: raise ValueError("Chain validation failed: " + why)
    balances, _, _ = balances_and_nonces(chain)
    print(f"Address: {address}\nBalance: {fmt(balances.get(address, 0))} NVRX")


def post_json(url: str, payload: dict, timeout: float = 3.0) -> dict:
    data = canonical(payload)
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "User-Agent": "NURVEX-testnet/0.3"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        raw = response.read(1_000_001)
        if len(raw) > 1_000_000:
            raise ValueError("Peer response too large")
        return json.loads(raw.decode("utf-8"))


def relay_to_peers(path: str, payload: dict) -> None:
    for peer in load_json(PEERS_FILE, []):
        try:
            post_json(peer.rstrip("/") + path, payload, timeout=2.0)
        except Exception as exc:
            print(f"Peer relay failed for {peer}: {exc}")


def transaction_valid_for_mempool(tx: dict, chain: list[dict], mempool: list[dict]) -> tuple[bool, str]:
    if not verify_tx(tx):
        return False, "Invalid signature or transaction format"
    if not isinstance(tx.get("recipient"), str) or not tx["recipient"].startswith("nvrx1"):
        return False, "Invalid recipient address"
    if tx_id(tx) in {tx_id(t) for t in mempool if isinstance(t, dict)}:
        return False, "Duplicate transaction"
    balances, nonces, _ = balances_and_nonces(chain)
    pending = [t for t in mempool if verify_tx(t)]
    # Apply pending transactions in deterministic sender/nonce order to avoid overspending.
    pending.sort(key=lambda t: (t.get("sender", ""), t.get("nonce", 0), tx_id(t)))
    for item in pending:
        sender = item["sender"]
        if item["nonce"] != nonces.get(sender, 0) + 1 or balances.get(sender, 0) < item["amount"]:
            continue
        balances[sender] -= item["amount"]
        balances[item["recipient"]] = balances.get(item["recipient"], 0) + item["amount"]
        nonces[sender] = item["nonce"]
    sender = tx["sender"]
    if tx["nonce"] != nonces.get(sender, 0) + 1:
        return False, "Unexpected nonce"
    if balances.get(sender, 0) < tx["amount"]:
        return False, "Insufficient confirmed/pending balance"
    return True, "OK"


def send_cmd(wallet_path: str, recipient: str, amount_text: str) -> None:
    chain = load_chain(); ok, why = validate_chain(chain)
    if not ok: raise ValueError("Chain validation failed: " + why)
    wallet = wallet_read(wallet_path)
    amount = amount_to_units(amount_text)
    balances, nonces, _ = balances_and_nonces(chain)
    mempool = load_json(MEMPOOL_FILE, [])
    # Reserve pending amounts and nonces from this sender.
    sender = wallet["address"]
    pending = [t for t in mempool if t.get("sender") == sender and verify_tx(t)]
    pending.sort(key=lambda t: t["nonce"])
    pending_spent = sum(t["amount"] for t in pending)
    nonce = nonces.get(sender, 0) + len(pending) + 1
    if balances.get(sender, 0) - pending_spent < amount: raise ValueError("Insufficient confirmed balance (mining rewards are not spendable until mined)")
    tx = {"type": "transfer", "sender": sender, "recipient": recipient, "amount": amount, "nonce": nonce, "public_key": wallet["public_key_hex"]}
    private = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(wallet["private_key_hex"]))
    tx["signature"] = private.sign(canonical(tx)).hex()
    mempool.append(tx); save_json(MEMPOOL_FILE, mempool)
    relay_to_peers("/transaction", tx)
    print(f"Transaction queued: {tx_id(tx)}\nFrom: {sender}\nTo: {recipient}\nAmount: {fmt(amount)} NVRX\nStatus: pending; relayed to configured peers when reachable; not yet confirmed")


def mine_cmd(miner_address: str) -> None:
    if not miner_address.startswith("nvrx1"): raise ValueError("Use an NURVEX address beginning with nvrx1")
    chain = load_chain(); ok, why = validate_chain(chain)
    if not ok: raise ValueError("Chain validation failed: " + why)
    _, _, issued = balances_and_nonces(chain)
    height = len(chain)
    subsidy = min(reward_for_height(height), MAX_SUPPLY - issued)
    if subsidy <= 0: raise ValueError("Maximum supply reached")
    mempool = load_json(MEMPOOL_FILE, [])
    balances, nonces, _ = balances_and_nonces(chain)
    valid_txs = []
    # Validate mempool transactions sequentially against a temporary ledger.
    for tx in mempool:
        if not verify_tx(tx): continue
        sender = tx["sender"]
        if tx["nonce"] != nonces.get(sender, 0) + 1 or balances.get(sender, 0) < tx["amount"]: continue
        balances[sender] -= tx["amount"]
        balances[tx["recipient"]] = balances.get(tx["recipient"], 0) + tx["amount"]
        nonces[sender] = tx["nonce"]
        valid_txs.append(tx)
    block = {"height": height, "timestamp": int(time.time()), "previous_hash": chain[-1]["hash"], "transactions": [{"type": "coinbase", "recipient": miner_address, "amount": subsidy}] + valid_txs, "nonce": 0, "protocol": PROTOCOL}
    started = time.time()
    while True:
        digest = block_hash(block)
        if digest.startswith(required_prefix(chain)):
            block["hash"] = digest; break
        block["nonce"] += 1
    chain.append(block)
    ok, why = validate_chain(chain)
    if not ok: raise ValueError("Mined block rejected by validator: " + why)
    save_chain(chain)
    included = {tx_id(t) for t in valid_txs}
    save_json(MEMPOOL_FILE, [t for t in mempool if tx_id(t) not in included])
    relay_to_peers("/block", block)
    print(f"Mined block #{height}: {block['hash']}\nReward: {fmt(subsidy)} NVRX\nTransactions: {len(valid_txs)}\nTime: {time.time()-started:.2f}s")


def discover_peers() -> int:
    """Ask known peers about their peers, merge new ones into local peers.json."""
    known = load_json(PEERS_FILE, [])
    discovered: set[str] = set()
    for peer in known:
        try:
            req = urllib.request.Request(peer.rstrip("/") + "/peers", headers={"User-Agent": "NURVEX-testnet/0.3"})
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode("utf-8"))
                for p in data.get("peers", []):
                    if isinstance(p, str) and p.startswith(("http://", "https://")):
                        discovered.add(p.rstrip("/"))
        except Exception:
            pass
    added = 0
    for url in discovered:
        if url not in known:
            known.append(url)
            added += 1
    if added:
        save_json(PEERS_FILE, known)
    return added


FAUCET_WALLET_FILE = DATA / "faucet_wallet.json"
FAUCET_AMOUNT = 10 * 100_000_000
FAUCET_COOLDOWN = 3600
FAUCET_LOG_FILE = DATA / "faucet_log.json"


def faucet_init_cmd():
    if FAUCET_WALLET_FILE.exists():
        wallet = wallet_read(str(FAUCET_WALLET_FILE))
        print("Faucet wallet already exists.")
        print("Address: " + wallet["address"])
        print("File: " + str(FAUCET_WALLET_FILE))
        return
    private = Ed25519PrivateKey.generate()
    priv_raw = private.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())
    pub_raw = private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    wallet = {"network": PROTOCOL, "private_key_hex": priv_raw.hex(), "public_key_hex": pub_raw.hex(), "address": address_for(pub_raw.hex()), "warning": "Faucet wallet. Testnet only."}
    FAUCET_WALLET_FILE.parent.mkdir(parents=True, exist_ok=True)
    FAUCET_WALLET_FILE.write_text(json.dumps(wallet, indent=2), encoding="utf-8")
    try: os.chmod(FAUCET_WALLET_FILE, 0o600)
    except OSError: pass
    print("Faucet wallet created: " + str(FAUCET_WALLET_FILE))
    print("Address: " + wallet["address"])
    print("")
    print("Next steps:")
    print("  1. Mine blocks to this address to fund the faucet")
    print("  2. Run serve to enable /faucet endpoint")


def faucet_request(recipient):
    if not isinstance(recipient, str) or not recipient.startswith("nvrx1"):
        return {"ok": False, "error": "Invalid NVRX address"}
    if not FAUCET_WALLET_FILE.exists():
        return {"ok": False, "error": "Faucet not configured"}
    wallet = wallet_read(str(FAUCET_WALLET_FILE))
    now = int(time.time())
    log = load_json(FAUCET_LOG_FILE, {})
    last = log.get(recipient, 0)
    if now - last < FAUCET_COOLDOWN:
        wait = FAUCET_COOLDOWN - (now - last)
        return {"ok": False, "error": "Cooldown active", "wait_seconds": wait}
    chain = load_chain(); ok, why = validate_chain(chain)
    if not ok:
        return {"ok": False, "error": "Chain invalid"}
    balances, nonces, _ = balances_and_nonces(chain)
    mempool = load_json(MEMPOOL_FILE, [])
    sender = wallet["address"]
    pending = [t for t in mempool if t.get("sender") == sender and verify_tx(t)]
    pending.sort(key=lambda t: t["nonce"])
    pending_spent = sum(t["amount"] for t in pending)
    balance = balances.get(sender, 0) - pending_spent
    if balance < FAUCET_AMOUNT:
        return {"ok": False, "error": "Faucet empty"}
    nonce = nonces.get(sender, 0) + len(pending) + 1
    tx = {"type": "transfer", "sender": sender, "recipient": recipient, "amount": FAUCET_AMOUNT, "nonce": nonce, "public_key": wallet["public_key_hex"]}
    private = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(wallet["private_key_hex"]))
    tx["signature"] = private.sign(canonical(tx)).hex()
    mempool.append(tx); save_json(MEMPOOL_FILE, mempool)
    log[recipient] = now; save_json(FAUCET_LOG_FILE, log)
    relay_to_peers("/transaction", tx)
    return {"ok": True, "txid": tx_id(tx), "amount": fmt(FAUCET_AMOUNT), "recipient": recipient}


def add_peer(url: str) -> None:
    url = url.rstrip("/")
    if not url.startswith(("http://", "https://")): raise ValueError("Peer must start with http:// or https://")
    peers = load_json(PEERS_FILE, [])
    if url not in peers: peers.append(url)
    save_json(PEERS_FILE, peers)
    print(f"Peer saved: {url}")


def sync_cmd() -> None:
    peers = load_json(PEERS_FILE, [])
    if not peers:
        print("No peers configured. Use: python nurvex_node.py add-peer http://HOST:PORT")
        return
    chain = load_chain(); current_height = len(chain) - 1
    for peer in peers:
        try:
            req = urllib.request.Request(peer + "/chain", headers={"User-Agent": "NURVEX-testnet/0.3"})
            with urllib.request.urlopen(req, timeout=5) as response:
                candidate = json.loads(response.read().decode("utf-8"))
            if not isinstance(candidate, list):
                print(f"Skipped {peer}: invalid response")
                continue
            ok, why = validate_chain(candidate)
            if not ok:
                print(f"Skipped {peer}: chain invalid ({why})")
                continue
            if len(candidate) > len(chain):
                chain = candidate
                save_chain(chain)
                current_height = len(chain) - 1
                print(f"Synced from {peer}; new height {current_height}")
            else:
                print(f"Peer {peer}: height {len(candidate)-1}; local height {current_height}")
        except Exception as exc:
            print(f"Could not sync {peer}: {exc}")
    try:
        added = discover_peers()
        if added > 0:
            print(f"Discovered {added} new peer(s).")
    except Exception as exc:
        print(f"Peer discovery failed: {exc}")


def sync_loop_cmd(interval: int) -> None:
    """Periodically ask configured peers for a valid longer chain. Testnet only."""
    if interval < 5:
        raise ValueError("Sync interval must be at least 5 seconds")
    print(f"NURVEX experimental sync loop started; interval={interval}s")
    print("Warning: plain HTTP peer protocol. Use only on a trusted LAN/VPN; do not port-forward to the public internet.")
    try:
        while True:
            sync_cmd()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nSync loop stopped.")


def serve_cmd(host: str, port: int) -> None:
    class Handler(BaseHTTPRequestHandler):
        def _reply(self, code: int, payload: dict) -> None:
            body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            self.send_response(code); self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

        def do_GET(self):
            if self.path == "/status" or self.path == "/health":
                chain = load_chain(); ok, why = validate_chain(chain)
                _, _, issued = balances_and_nonces(chain)
                payload = {"project": "NURVEX", "protocol": PROTOCOL, "height": len(chain)-1, "issued": fmt(issued), "maximum_supply": "18000000", "chain_valid": ok, "validation": why, "production_ready": False}
            elif self.path == "/peers":
                payload = {"peers": load_json(PEERS_FILE, [])}
            elif self.path == "/chain":
                payload = load_chain()
            elif self.path == "/mempool":
                payload = load_json(MEMPOOL_FILE, [])
            elif self.path == "/faucet":
                if FAUCET_WALLET_FILE.exists():
                    chain = load_chain()
                    balances, _, _ = balances_and_nonces(chain)
                    fw = wallet_read(str(FAUCET_WALLET_FILE))
                    mempool = load_json(MEMPOOL_FILE, [])
                    pending_out = sum(t["amount"] for t in mempool if t.get("sender") == fw["address"] and verify_tx(t))
                    available = balances.get(fw["address"], 0) - pending_out
                    payload = {"ok": True, "address": fw["address"], "balance": fmt(balances.get(fw["address"], 0)), "available": fmt(available), "pending_out": fmt(pending_out), "amount_per_request": fmt(FAUCET_AMOUNT), "cooldown_seconds": FAUCET_COOLDOWN}
                else:
                    payload = {"ok": False, "error": "Faucet not configured. Run: faucet-init"}
            else:
                self.send_error(404); return
            body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            self.send_response(200); self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

        def do_POST(self):
            if self.path not in ("/transaction", "/block", "/faucet"):
                self._reply(404, {"ok": False, "error": "Unknown endpoint"}); return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if size <= 0 or size > 1_000_000:
                    self._reply(413, {"ok": False, "error": "Invalid payload size"}); return
                payload = json.loads(self.rfile.read(size).decode("utf-8"))
                if self.path == "/faucet":
                    addr = payload.get("address")
                    result = faucet_request(addr)
                    self._reply(200 if result.get("ok") else 400, result); return
                if self.path == "/transaction":
                    chain = load_chain(); ok, why = validate_chain(chain)
                    if not ok: raise ValueError("Local chain invalid: " + why)
                    mempool = load_json(MEMPOOL_FILE, [])
                    valid, why = transaction_valid_for_mempool(payload, chain, mempool)
                    if not valid:
                        self._reply(409, {"ok": False, "error": why}); return
                    mempool.append(payload); save_json(MEMPOOL_FILE, mempool)
                    self._reply(200, {"ok": True, "id": tx_id(payload), "status": "pending"})
                    relay_to_peers("/transaction", payload)
                    return
                if not isinstance(payload, dict): raise ValueError("Block must be an object")
                chain = load_chain(); ok, why = validate_chain(chain)
                if not ok: raise ValueError("Local chain invalid: " + why)
                if payload.get("previous_hash") != chain[-1].get("hash"):
                    self._reply(409, {"ok": False, "error": "Block does not extend local tip; run sync"}); return
                candidate = chain + [payload]
                valid, why = validate_chain(candidate)
                if not valid:
                    self._reply(400, {"ok": False, "error": why}); return
                save_chain(candidate)
                included = {tx_id(t) for t in payload.get("transactions", []) if isinstance(t, dict)}
                save_json(MEMPOOL_FILE, [t for t in load_json(MEMPOOL_FILE, []) if tx_id(t) not in included])
                self._reply(200, {"ok": True, "height": payload["height"], "hash": payload["hash"]})
                relay_to_peers("/block", payload)
            except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
                self._reply(400, {"ok": False, "error": str(exc)})

        def log_message(self, fmt_string, *args):
            print("[http] " + (fmt_string % args))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"NURVEX prototype node listening at http://{host}:{port}")
    print("Endpoints: /status, /health, /peers, /chain, /mempool, /transaction, /block. Testnet only; no TLS or peer authentication.")
    try: server.serve_forever()
    except KeyboardInterrupt: print("Stopping node...")
    finally: server.server_close()


def status_cmd() -> None:
    chain = load_chain(); ok, why = validate_chain(chain)
    _, _, issued = balances_and_nonces(chain)
    print(json.dumps({"project": "NURVEX", "ticker_proposed": "NVRX", "protocol": PROTOCOL, "blocks": len(chain), "height": len(chain)-1, "issued": fmt(issued), "maximum_supply": "18000000", "mempool_transactions": len(load_json(MEMPOOL_FILE, [])), "chain_valid": ok, "validation": why, "network": "experimental HTTP peer sync; not production-ready", "peers": load_json(PEERS_FILE, []), "production_ready": False}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="NURVEX local testnet prototype")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="Initialize local chain")
    sub.add_parser("status", help="Show chain status")
    sub.add_parser("validate", help="Validate all blocks")
    p = sub.add_parser("add-peer", help="Save an HTTP peer URL"); p.add_argument("url")
    sub.add_parser("sync", help="Try to adopt a valid longer chain from configured peers")
    sl = sub.add_parser("sync-loop", help="Periodically synchronize from configured peers (testnet only)"); sl.add_argument("--interval", type=int, default=15)
    srv = sub.add_parser("serve", help="Serve testnet chain and relay endpoints"); srv.add_argument("--host", default="127.0.0.1"); srv.add_argument("--port", type=int, default=8338)
    w = sub.add_parser("wallet", help="Create a new wallet file"); w.add_argument("path")
    b = sub.add_parser("balance", help="Check an address balance"); b.add_argument("address")
    m = sub.add_parser("mine", help="Mine one local block"); m.add_argument("address")
    s = sub.add_parser("send", help="Sign and queue a transfer"); s.add_argument("wallet"); s.add_argument("recipient"); s.add_argument("amount")
    sub.add_parser("faucet-init", help="Create the faucet wallet (testnet)")
    args = parser.parse_args()
    try:
        if args.command == "init": init()
        elif args.command == "status": status_cmd()
        elif args.command == "add-peer": add_peer(args.url)
        elif args.command == "sync": sync_cmd()
        elif args.command == "sync-loop": sync_loop_cmd(args.interval)
        elif args.command == "serve": serve_cmd(args.host, args.port)
        elif args.command == "validate":
            ok, why = validate_chain(load_chain()); print(f"Valid: {ok}\nResult: {why}"); sys.exit(0 if ok else 1)
        elif args.command == "wallet": new_wallet(args.path)
        elif args.command == "balance": balance_cmd(args.address)
        elif args.command == "mine": mine_cmd(args.address)
        elif args.command == "send": send_cmd(args.wallet, args.recipient, args.amount)
        elif args.command == "faucet-init": faucet_init_cmd()
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr); sys.exit(1)

if __name__ == "__main__": main()
