#!/bin/bash
# Disable api_server on Shima (no API_SERVER_KEY; it kills the gateway on failure).
# Then restart her gateway cleanly.
qm guest exec 123 -- python3 - <<'PY'
import re
p='/home/shima/.hermes/config.yaml'
s=open(p).read()
# find platforms.api_server.enabled: true and set false
s2=re.sub(r'(api_server:\s*\n\s*enabled:\s*)true', r'\1false', s, count=1)
open(p,'w').write(s2)
print('api_server now:', 'enabled: false' in s2.split('api_server:')[1][:80])
PY
# restart gateway via guest agent (pkill + systemd start, separate process)
qm guest exec 123 -- bash -c "
  pkill -u shima -f 'hermes gateway' 2>/dev/null || true
  sleep 3
  systemctl start hermes-gateway
  sleep 2
  echo ACTIVE=\$(systemctl is-active hermes-gateway)
  echo PROC=\$(pgrep -c -u shima -f 'hermes gateway')
" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('out-data','').replace('\\\\n','\n'))" 2>/dev/null
echo SHIMA_FIX_DONE
