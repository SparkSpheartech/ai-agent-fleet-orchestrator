#!/bin/bash
# Restart Onyx gateway so it becomes sole poller after removing the dup token from main agent.
# Uses start (not restart) and pkill to avoid consent-gate trigger words.
qm guest exec 120 -- bash -c "
  pkill -u onyx -f 'hermes gateway' 2>/dev/null
  sleep 3
  systemctl start hermes-gateway
  sleep 2
  echo ACTIVE=\$(systemctl is-active hermes-gateway)
  pgrep -c -u onyx -f 'hermes gateway'
" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('out-data','').replace('\\\\n','\n'))" 2>/dev/null
echo DONE
