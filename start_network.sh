#!/data/data/com.termux/files/usr/bin/bash
# NURVEX local testnet launcher — 3 nodes
set -e
cd "$(dirname "$0")"
BASE=~/nurvex_net
mkdir -p $BASE

# Init 3 nodes if not initialized
for i in 1 2 3; do
  DIR=$BASE/node$i
  if [ ! -f "$DIR/chain.json" ]; then
    echo "→ Initializing node$i..."
    NURVEX_DATA_DIR=$DIR python nurvex_node.py init
    NURVEX_DATA_DIR=$DIR python nurvex_node.py wallet $DIR/wallet.json
  fi
done

# Node1: bootstrap (port 8765)
NURVEX_DATA_DIR=$BASE/node1 python nurvex_node.py serve --host 127.0.0.1 --port 8765 > $BASE/node1.log 2>&1 &
echo "Node1 PID $! → :8765"

sleep 2

# Node2: peer of node1 (port 8766)
NURVEX_DATA_DIR=$BASE/node2 python nurvex_node.py add-peer http://127.0.0.1:8765
NURVEX_DATA_DIR=$BASE/node2 python nurvex_node.py serve --host 127.0.0.1 --port 8766 > $BASE/node2.log 2>&1 &
echo "Node2 PID $! → :8766"

# Node3: peer of node1 (port 8767)
NURVEX_DATA_DIR=$BASE/node3 python nurvex_node.py add-peer http://127.0.0.1:8765
NURVEX_DATA_DIR=$BASE/node3 python nurvex_node.py serve --host 127.0.0.1 --port 8767 > $BASE/node3.log 2>&1 &
echo "Node3 PID $! → :8767"

echo ""
echo "✅ Testnet running. Logs in $BASE/*.log"
echo "Stop with: pkill -f nurvex_node.py"
