#!/data/data/com.termux/files/usr/bin/bash
pkill -f "nurvex_node.py serve" 2>/dev/null
pkill -f "nurvex_node.py sync-loop" 2>/dev/null
sleep 1
REMAIN=$(pgrep -f nurvex_node.py | wc -l)
if [ "$REMAIN" -eq 0 ]; then
  echo "✅ All NURVEX nodes stopped"
else
  echo "⚠️  $REMAIN processes remaining:"
  pgrep -af nurvex_node.py
fi
