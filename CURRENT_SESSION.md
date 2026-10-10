# NURVEX — Current Session State

**Saved at:** $(date)
**Session:** 2 (with faucet on internet)

## Running Processes

- SSH Tunnel: localhost.run → 8765
- Node1 serve: :8765 (with faucet)
- Node2 serve: :8766
- Node3 serve: :8767

## Bootstrap URL

https://452f440293c541.lhr.life

## Faucet

- Address: nvrx1d109f6da8f2a98c0f83974e66bd7e77f76a60959
- Balance: ~32.85 NVRX
- Amount per request: 10 NVRX
- Cooldown: 3600s

## Node Addresses

- Node1: nvrx1c6ef3c7871269bb0c4997a8599fd4c7381156636
- Node2: nvrx12794457b6b35cf2a4533ce356a55b8cfc987b224
- Node3: nvrx1773b3b9ad226dad11ebcb9caf0a65408a2df9330

## Last Commit

3a858c6 docs: add BOOTSTRAP.md with permanent URL

## To Stop Everything

pkill -f nurvex_node.py; pkill -f ssh

## To Resume

# Start SSH tunnel (in session A):
ssh -i ~/.ssh/id_ed25519 -R 80:localhost:8765 localhost.run

# Start Node1 serve (in session B):
NURVEX_DATA_DIR=~/nurvex_net/node1 python ~/NURVEX_NODE2/nurvex_node.py serve --host 127.0.0.1 --port 8765

## To Verify Everything Works

curl -s https://452f440293c541.lhr.life/status
curl -s https://452f440293c541.lhr.life/faucet
