# NURVEX Node

> Experimental blockchain testnet written in pure Python.

## What is NURVEX?

NURVEX is a lightweight blockchain testnet that implements:

- Proof-of-Work consensus with dynamic difficulty (target: 60s/block).
- Ed25519 transaction signatures.
- HTTP peer-to-peer gossip (block and transaction propagation).
- Peer Discovery - nodes learn about each other automatically.
- Faucet - anyone can get NVRX to test the network.
- REST API - status, blocks, transactions, peers, faucet.

WARNING: Not production-ready. Testnet only. NVRX has no real value.

## Quick Start

    pip install -r requirements.txt
    export NURVEX_DATA_DIR=~/nurvex_net/mynode
    python nurvex_node.py init
    python nurvex_node.py wallet $NURVEX_DATA_DIR/wallet.json
    python nurvex_node.py add-peer http://BOOTSTRAP_HOST:8338
    python nurvex_node.py sync
    python nurvex_node.py mine YOUR_ADDRESS
    python nurvex_node.py serve --host 0.0.0.0 --port 8338

## Documentation

- docs/SETUP.md - run a node from scratch
- docs/ARCHITECTURE.md - how NURVEX works internally
- docs/API.md - all HTTP endpoints with examples
- docs/MINING.md - PoW, difficulty, expected times
- docs/DEPLOYMENT.md - expose your node to the internet (free, no VPS)

## Features

| Feature | Status |
|---|---|
| PoW mining | Done |
| Dynamic difficulty | Done |
| Ed25519 signatures | Done |
| Mempool + sequential validation | Done |
| Peer discovery (gossip) | Done |
| Faucet (10 NVRX/hour) | Done |
| REST API | Done |
| Timestamp validation | Done |
| Halving | Done |
| Max supply cap (18M) | Done |
| Fork resolution | Planned |
| TLS P2P | Planned |
| Web block explorer | Planned |

## Constants

| Name | Value |
|---|---|
| Protocol | NURVEX-TESTNET-0.3 |
| Ticker | NVRX |
| Max supply | 18,000,000 NVRX |
| Initial reward | 8.57142857 NVRX |
| Halving interval | 1,050,000 blocks |
| Target block time | 60 s |
| Difficulty | 5-8 leading zeros |
| Faucet amount | 10 NVRX |
| Faucet cooldown | 3600 s |

## CLI Commands

| Command | Description |
|---|---|
| init | Initialize local chain |
| status | Show chain status |
| validate | Validate all blocks |
| wallet <path> | Create a new wallet |
| balance <address> | Check address balance |
| mine <address> | Mine one local block |
| send <wallet> <recipient> <amount> | Sign and queue a transfer |
| add-peer <url> | Save an HTTP peer URL |
| sync | Sync chain from peers |
| sync-loop --interval N | Auto-sync periodically |
| serve --host H --port P | Start HTTP server |
| faucet-init | Create the faucet wallet |

## HTTP API

See docs/API.md for full details.

| Method | Path | Description |
|---|---|---|
| GET | /status | Chain height, issued supply, validity |
| GET | /health | Alias for /status |
| GET | /peers | Known peer list |
| GET | /chain | Full chain |
| GET | /blocks?from=X&limit=N | Paginated blocks |
| GET | /mempool | Pending transactions |
| GET | /tx/{txid} | Transaction lookup |
| GET | /faucet | Faucet status |
| POST | /transaction | Relay a signed transaction |
| POST | /block | Relay a mined block |
| POST | /peer | Add a peer |
| POST | /faucet | Request NVRX from faucet |

## Requirements

- Python 3.10+
- pip
- cryptography library (installed via requirements.txt)

## Platform Support

- Linux: yes
- macOS: yes
- Windows (WSL2): yes
- Android (Termux): yes
- iOS: not tested

## Security

- No TLS on P2P (testnet only).
- No peer authentication - anyone can join.
- Backup your wallet (wallet.json) - losing it means losing funds.
- Do not expose to the public internet without additional hardening.

## License

TBD. Testnet prototype.

---

Reminder: NURVEX is an experimental testnet. NVRX has no monetary value.
