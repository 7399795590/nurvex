#!/data/data/com.termux/files/usr/bin/bash
# Live NURVEX network monitor
PORTS="8765 8766 8767"
while true; do
  clear
  echo "=== NURVEX Monitor — $(date +%H:%M:%S) ==="
  printf "%-8s %-10s %-15s %-10s\n" "NODE" "HEIGHT" "ISSUED" "VALID"
  for p in $PORTS; do
    DATA=$(curl -s --max-time 2 http://127.0.0.1:$p/status 2>/dev/null)
    if [ -z "$DATA" ]; then
      printf "%-8s %-10s %-15s %-10s\n" ":$p" "DOWN" "-" "-"
    else
      H=$(echo "$DATA" | python -c "import sys,json;print(json.load(sys.stdin)['height'])" 2>/dev/null)
      I=$(echo "$DATA" | python -c "import sys,json;print(json.load(sys.stdin)['issued'])" 2>/dev/null)
      V=$(echo "$DATA" | python -c "import sys,json;print(json.load(sys.stdin)['chain_valid'])" 2>/dev/null)
      printf "%-8s %-10s %-15s %-10s\n" ":$p" "$H" "$I" "$V"
    fi
  done
  echo ""
  echo "Press Ctrl+C to stop. Refreshing every 3s..."
  sleep 3
done
