#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")"
BASE=~/nurvex_net

echo "🧪 NURVEX Network Test Suite"
echo "=============================="

# Test 1: Nodes alive
echo ""
echo "TEST 1: Nodes alive?"
for p in 8765 8766 8767; do
  H=$(curl -s --max-time 2 http://127.0.0.1:$p/status | python -c "import sys,json;print(json.load(sys.stdin)['height'])" 2>/dev/null || echo "DOWN")
  echo "  :$p → height=$H"
done

# Test 2: Chain consistency
echo ""
echo "TEST 2: Chain consistency"
H1=$(curl -s http://127.0.0.1:8765/status | python -c "import sys,json;print(json.load(sys.stdin)['height'])")
H2=$(curl -s http://127.0.0.1:8766/status | python -c "import sys,json;print(json.load(sys.stdin)['height'])")
H3=$(curl -s http://127.0.0.1:8767/status | python -c "import sys,json;print(json.load(sys.stdin)['height'])")
if [ "$H1" = "$H2" ] && [ "$H2" = "$H3" ]; then
  echo "  ✅ All nodes at height $H1"
else
  echo "  ❌ MISMATCH: $H1 / $H2 / $H3"
fi

# Test 3: Wallet balance
echo ""
echo "TEST 3: Wallet balance on node1"
ADDR1=$(python -c "import json;print(json.load(open('$BASE/node1/wallet.json'))['address'])")
BAL=$(NURVEX_DATA_DIR=$BASE/node1 python nurvex_node.py balance $ADDR1 | grep Balance | awk '{print $2}')
echo "  ADDR1 balance: $BAL NVRX"

# Test 4: Mine + propagate
echo ""
echo "TEST 4: Mine + propagate"
BEFORE=$H1
NURVEX_DATA_DIR=$BASE/node1 python nurvex_node.py mine $ADDR1 > /dev/null
NURVEX_DATA_DIR=$BASE/node2 python nurvex_node.py sync > /dev/null
NURVEX_DATA_DIR=$BASE/node3 python nurvex_node.py sync > /dev/null
AFTER=$(curl -s http://127.0.0.1:8766/status | python -c "import sys,json;print(json.load(sys.stdin)['height'])")
if [ "$AFTER" -gt "$BEFORE" ]; then
  echo "  ✅ Block mined and propagated: $BEFORE → $AFTER"
else
  echo "  ❌ Propagation failed: $BEFORE → $AFTER"
fi

echo ""
echo "=============================="
echo "✅ Test suite complete"
