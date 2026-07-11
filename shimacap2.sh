#!/bin/bash
qm guest exec 123 -- bash -c "
  cd /home/shima
  pkill -u shima -f 'hermes gateway' 2>/dev/null || true
  sleep 2
  timeout 18 /usr/local/lib/hermes-agent/venv/bin/hermes gateway > /tmp/shima_gw.log 2>&1
  echo '=== EXIT: '\$?' ==='
  echo '=== TAIL 45 ==='
  tail -45 /tmp/shima_gw.log
" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('out-data','').replace('\\\\n','\n'))" 2>/dev/null
echo CAPTURE_DONE
