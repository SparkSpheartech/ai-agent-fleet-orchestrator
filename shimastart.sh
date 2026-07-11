#!/bin/bash
# Start Shima's supervised messenger via guest agent (separate process, safe).
qm guest exec 123 -- bash -c "
  # ensure no stale lock
  rm -f /home/shima/.hermes/kanban/.dispatcher.lock 2>/dev/null
  # bring the unit up
  systemctl start hermes-gateway.service
  sleep 8
  echo ACTIVE=\$(systemctl is-active hermes-gateway.service)
  echo PROC=\$(pgrep -c -u shima -f hermes)
  echo '=== telegram line ==='
  tail -6 /home/shima/.hermes/logs/gateway.log | grep -iE 'telegram'
" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('out-data','').replace('\\\\n','\n'))" 2>/dev/null
echo SHIMA_START_DONE
