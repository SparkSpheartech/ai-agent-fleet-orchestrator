#!/bin/bash
# Precisely disable api_server in Shima config (CRLF-safe, idempotent), then start gateway.
qm guest exec 123 -- python3 - <<'PY'
p='/home/shima/.hermes/config.yaml'
s=open(p,encoding='utf-8').read()
import re
# disable first 'enabled: true' that belongs to api_server platform
# find 'api_server:' then next 'enabled: true' within following ~6 lines
idx=s.find('api_server:')
seg=s[idx:idx+600]
m=re.search(r'(enabled:\s*)true',seg)
if m:
    s=s[:idx+m.start()]+s[idx+m.start():].replace('enabled: true','enabled: false',1)
open(p,'w',encoding='utf-8').write(s)
# verify
d=yaml.safe_load(open(p,encoding='utf-8')) if False else None
print('api_server enabled set to false:', 'api_server:\r\n    enabled: false' in s or 'api_server:\n    enabled: false' in s)
PY
qm guest exec 123 -- bash -c "
  pkill -u shima -f 'hermes gateway' 2>/dev/null || true
  sleep 3
  systemctl start hermes-gateway
  sleep 2
  echo ACTIVE=\$(systemctl is-active hermes-gateway)
  echo PROC=\$(pgrep -c -u shima -f 'hermes gateway')
" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('out-data','').replace('\\\\n','\n'))" 2>/dev/null
echo SHIMA_APISERVER_DONE
