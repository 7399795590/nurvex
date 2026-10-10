# NURVEX Architecture

## Overview

NURVEX is a lightweight blockchain testnet written in pure Python.
It implements Proof-of-Work consensus with dynamic difficulty,
Ed25519 transaction signatures, and HTTP-based peer-to-peer gossip.

## Core Components

### 1. Chain

- Stored in `chain.json` per node.
- Structure: list of blocks.
- Block: `{height, timestamp, previous_hash, transactions, nonce, protocol, hash}`
- Genesis block: height 0, timestamp 0.

### 2. Consensus

- **Rule:** Longest valid chain wins.
- **Validation:** Every block hash must start with `N` zeros (N = current difficulty).
- **Dynamic difficulty:** Adjusts every 10 blocks, target 60s/block.

### 3. Transactions

- Type: `transfer` only (currently).
- Signature: Ed25519.
- Amount: integer, in smallest units (1 NVRX = 100,000,000 units).
- Nonce: per-sender, monotonic, prevents replay.

### 4. Mempool

- File: `mempool.json`.
- Pending transactions, waiting for mining.
- Validation: sequential per-sender nonce order.

### 5. Mining

- Command: `mine <address>`.
- Finds nonce where `sha256(block)` starts with required zeros.
- Includes valid mempool transactions.
- Reward: current subsidy (halving every 1,050,000 blocks).

### 6. P2P Network

- Protocol: HTTP/1.1 (plain, no TLS — testnet only).
- Peers: stored in `peers.json`.
- Gossip: transactions and blocks relayed to all peers.
- **Peer Discovery:** each node asks known peers about their peers, merges new ones.

### 7. Faucet

- Optional HTTP service.
- Wallet: `faucet_wallet.json`.
- Endpoint: `POST /faucet` with `{"address": "..."}`.
- Rate limit: 1 request per hour per address.
- Amount: 10 NVRX per request.

## Constants

| Name | Value | Meaning |
|---|---|---|
| `COIN` | 100,000,000 | Smallest unit per NVRX |
| `MAX_SUPPLY` | 18,000,000 NVRX | Total supply cap |
| `INITIAL_REWARD` | 8.57142857 NVRX | First mining subsidy |
| `HALVING_INTERVAL` | 1,050,000 | Blocks between halvings |
| `TARGET_BLOCK_TIME` | 60 | Seconds per block (target) |
| `DIFFICULTY_ADJUST_INTERVAL` | 10 | Blocks between adjustments |
| `MIN_DIFFICULTY` | 5 | Minimum leading zeros |
| `MAX_DIFFICULTY` | 8 | Maximum leading zeros |
| `MAX_FUTURE_DRIFT` | 7200 | Max seconds in future for timestamp |
| `MAX_PAST_DRIFT` | 7200 | Max seconds in past for timestamp |
| `FAUCET_AMOUNT` | 10 NVRX | Amount per faucet request |
| `FAUCET_COOLDOWN` | 3600 | Seconds between faucet requests |
| `PROTOCOL` | "NURVEX-TESTNET-0.3" | Network identifier |

## File Layout

\`\`\`
~/.nurvex_net/nodeX/
  chain.json         # blockchain
  mempool.json       # pending transactions
  peers.json         # known peer URLs
  wallet.json        # node's wallet (if created)
  faucet_wallet.json # faucet wallet (if created)
  faucet_log.json    # faucet request log (cooldown)
\`\`\`

## Limitations

- No fork resolution beyond longest-chain rule.
- No P2P authentication (anyone can join — by design for testnet).
- No TLS (testnet only; do NOT port-forward to public internet without TLS).
- Single-threaded mining (no GPU/ASIC support).

## Future Work

- Fork resolution (equal-length chains).
- TLS support for P2P.
- Multi-transaction types (tokens, smart contracts).
- Light clients / SPV proofs.
- Testnet block explorer (web UI).
