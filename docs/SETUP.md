# NURVEX Node — Setup Guide

This guide explains how to run a NURVEX testnet node from scratch.

## Requirements

- Python 3.10 or newer
- pip
- ~100 MB free disk space
- (Optional) A VPS or always-on device for 24/7 operation

## Install

### 1. Clone or copy the project

\`\`\`bash
git clone <repo-url> nurvex
cd nurvex
\`\`\`

Or if you received a folder:

\`\`\`bash
cd /path/to/NURVEX_NODE2
\`\`\`

### 2. Install dependencies

\`\`\`bash
pip install -r requirements.txt
\`\`\`

On Android/Termux:

\`\`\`bash
pkg install python git
pip install cryptography
\`\`\`

### 3. Initialize your node

Choose a data directory for your node (e.g. `~/nurvex_net/mynode`):

\`\`\`bash
export NURVEX_DATA_DIR=~/nurvex_net/mynode
python nurvex_node.py init
\`\`\`

This creates:
- `chain.json` (the blockchain)
- `mempool.json` (pending transactions)
- `peers.json` (empty peer list)

### 4. Create your wallet

\`\`\`bash
python nurvex_node.py wallet $NURVEX_DATA_DIR/wallet.json
\`\`\`

**Save the address** printed. It looks like \`nvrx1...\`.
**Keep the wallet file secret.** Never share `private_key_hex`.

## Join the Network

### 1. Add a bootstrap peer

Ask the network operator for a bootstrap node URL, e.g. \`http://192.168.1.10:8765\`.

\`\`\`bash
python nurvex_node.py add-peer http://192.168.1.10:8765
\`\`\`

Or via HTTP:

\`\`\`bash
curl -X POST http://127.0.0.1:8338/peer \\
  -H "Content-Type: application/json" \\
  -d '{"url": "http://192.168.1.10:8765"}'
\`\`\`

### 2. Sync the chain

\`\`\`bash
python nurvex_node.py sync
\`\`\`

### 3. Start serving

\`\`\`bash
python nurvex_node.py serve --host 0.0.0.0 --port 8338
\`\`\`

Use \`0.0.0.0\` to accept connections from other devices on your LAN.

### 4. (Optional) Auto-sync loop

In another terminal:

\`\`\`bash
python nurvex_node.py sync-loop --interval 30
\`\`\`

## Get NVRX from the Faucet

Once your node is synced, request NVRX from a faucet node:

\`\`\`bash
curl -X POST http://FAUCET_HOST:8338/faucet \\
  -H "Content-Type: application/json" \\
  -d '{"address": "YOUR_NVRX_ADDRESS"}'
\`\`\`

You will receive 10 NVRX. Cooldown: 1 hour per address.

## Mine Your First Block

\`\`\`bash
python nurvex_node.py mine YOUR_NVRX_ADDRESS
\`\`\`

Expected time: 10–60 seconds (depends on difficulty and your CPU).

The reward (currently 8.57142857 NVRX) goes to your address after the block is accepted by the network.

## Send NVRX

\`\`\`bash
python nurvex_node.py send $NURVEX_DATA_DIR/wallet.json RECIPIENT_ADDRESS 1.5
\`\`\`

The transaction is queued locally and relayed to peers. It will be included in the next mined block.

## Check Status

\`\`\`bash
curl http://127.0.0.1:8338/status
curl http://127.0.0.1:8338/peers
curl http://127.0.0.1:8338/blocks?from=0&limit=5
\`\`\`

## Troubleshooting

### "Chain invalid"

\`\`\`bash
python nurvex_node.py validate
\`\`\`

If it fails, try re-syncing:

\`\`\`bash
python nurvex_node.py sync
\`\`\`

### "Faucet empty"

The faucet wallet needs NVRX. If you run the faucet, mine some blocks to it first.

### "Connection refused"

Your peer is offline or firewall blocks the port.

### Mining takes too long

- Normal: 10–60s at difficulty 5
- If > 5 minutes, your CPU may be overloaded. Close other apps.
- At difficulty 6, expect 5–10 minutes.

## Security Notes

- **Never port-forward to the public internet** without TLS. NURVEX testnet uses plain HTTP.
- **Backup your wallet** (`wallet.json`). If lost, funds are lost.
- **No real value.** NVRX is a testnet token. Do not trade it.
