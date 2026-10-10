# NURVEX Testnet Bootstrap

## Current Bootstrap Node

**URL:** https://452f440293c541.lhr.life

**Started:** 2026-10-10
**Protocol:** NURVEX-TESTNET-0.3
**Tunnel:** localhost.run (SSH-based, permanent URL)

## Endpoints

- `/status` — chain status
- `/peers` — known peers
- `/chain` — full chain
- `/blocks?from=X&limit=N` — paginated blocks
- `/tx/{txid}` — transaction lookup
- `/faucet` — faucet status
- `POST /faucet` — request NVRX

## How to Join

1. Install NURVEX:

       pip install -r requirements.txt

2. Create wallet:

       NURVEX_DATA_DIR=~/nurvex_net/mynode python nurvex_node.py init
       NURVEX_DATA_DIR=~/nurvex_net/mynode python nurvex_node.py wallet ~/nurvex_net/mynode/wallet.json

3. Add bootstrap peer:

       NURVEX_DATA_DIR=~/nurvex_net/mynode python nurvex_node.py add-peer https://452f440293c541.lhr.life

4. Sync:

       NURVEX_DATA_DIR=~/nurvex_net/mynode python nurvex_node.py sync

5. Request NVRX from faucet:

       curl -X POST https://452f440293c541.lhr.life/faucet \
         -H "Content-Type: application/json" \
         -d '{"address": "YOUR_NVRX_ADDRESS"}'

6. Start mining:

       NURVEX_DATA_DIR=~/nurvex_net/mynode python nurvex_node.py mine YOUR_NVRX_ADDRESS

## Notes

- Testnet only. NVRX has no real value.
- Faucet: 10 NVRX per hour per address.
- Bootstrap URL is permanent (SSH key-based).
- For more: docs/DEPLOYMENT.md
