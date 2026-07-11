#!/bin/bash
# Copy Daisy's working config to Shima, then inject Shima's token.
# Run Daisy's config fetch + Shima write via guest agent.
# Step 1: read Daisy config + env (masked check) into host temp
qm guest exec 121 -- bash -c "cat /home/daisy/.hermes/config.yaml" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); open('/root/shima_config.yaml','w').write(d.get('out-data','').replace('\\\\r\\\\n','\n').replace('\\\\n','\n'))" 2>/dev/null
echo "daisy config bytes: $(wc -c < /root/shima_config.yaml)"
# Step 2: push to Shima and swap token + home channel
TOKEN="8813962270:AAGnzgGQTXRe_JGr9k7YyNfc7AQHgPqxsRo"
qm guest exec 123 -- python3 - <<PY
import json
tok="$TOKEN"
cfg=open('/root/shima_config.yaml').read()
# ensure CRLF stripped -> LF (Hermes tolerates both, but be safe)
cfg=cfg.replace('\r\n','\n').replace('\r','\n')
open('/home/shima/.hermes/config.yaml','w').write(cfg)
# build .env from Daisy's but swap token
import subprocess
out=subprocess.run(['bash','-c',"grep -vE '^TELEGRAM_BOT_TOKEN=|^TELEGRAM_ALLOWED_USERS=|^TELEGRAM_HOME_CHANNEL=|^TELEGRAM_HOME_CHANNEL_NAME=' /home/daisy/.hermes/.env"],capture_output=True,text=True)
env=out.stdout
env+="TELEGRAM_BOT_TOKEN=%s\n"%tok
env+="TELEGRAM_ALLOWED_USERS=7018094108\n"
env+="TELEGRAM_HOME_CHANNEL=7018094108\n"
env+="TELEGRAM_HOME_CHANNEL_NAME=Shazaly\n"
open('/home/shima/.hermes/.env','w').write(env)
print("config written:", len(cfg), "env written:", len(env))
PY
# Step 3: restart
qm guest exec 123 -- bash -c "
  pkill -u shima -f 'hermes gateway' 2>/dev/null || true
  sleep 3
  systemctl start hermes-gateway
  sleep 2
  echo ACTIVE=\$(systemctl is-active hermes-gateway)
  echo PROC=\$(pgrep -c -u shima -f 'hermes gateway')
" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('out-data','').replace('\\\\n','\n'))" 2>/dev/null
echo SHIMA_CLONE_DONE
