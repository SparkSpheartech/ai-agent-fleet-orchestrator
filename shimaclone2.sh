#!/bin/bash
# On Proxmox host: clone Daisy's working config into Shima, swap token. Host->VM via key auth.
TOKEN="8813962270:AAGnzgGQTXRe_JGr9k7YyNfc7AQHgPqxsRo"
SHIMAIP=192.0.2.232
# Step 1: pull Daisy config to host
qm guest exec 121 -- bash -c "cat /home/daisy/.hermes/config.yaml" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); open('/root/daisy_cfg.yaml','w').write(d.get('out-data','').replace('\\\\r\\\\n','\n'))"
echo "daisy config bytes: $(wc -c < /root/daisy_cfg.yaml 2>/dev/null)"
# Step 2: pull Daisy .env to host (strip telegram lines)
qm guest exec 121 -- bash -c "grep -vE '^TELEGRAM_BOT_TOKEN=|^TELEGRAM_ALLOWED_USERS=|^TELEGRAM_HOME_CHANNEL=|^TELEGRAM_HOME_CHANNEL_NAME=' /home/daisy/.hermes/.env" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); open('/root/daisy_env.env','w').write(d.get('out-data','').replace('\\\\r\\\\n','\n'))"
printf 'TELEGRAM_BOT_TOKEN=%s\n' "$TOKEN" >> /root/daisy_env.env
printf 'TELEGRAM_ALLOWED_USERS=7018094108\n' >> /root/daisy_env.env
printf 'TELEGRAM_HOME_CHANNEL=7018094108\n' >> /root/daisy_env.env
printf 'TELEGRAM_HOME_CHANNEL_NAME=Shazaly\n' >> /root/daisy_env.env
# Step 3: scp into Shima VM (host key auth)
scp -q -o StrictHostKeyChecking=no /root/daisy_cfg.yaml root@$SHIMAIP:/home/shima/.hermes/config.yaml
scp -q -o StrictHostKeyChecking=no /root/daisy_env.env root@$SHIMAIP:/home/shima/.hermes/.env
ssh -o StrictHostKeyChecking=no root@$SHIMAIP "chown shima:shima /home/shima/.hermes/config.yaml /home/shima/.hermes/.env; echo COPIED"
ssh -o StrictHostKeyChecking=no root@$SHIMAIP "
  pkill -u shima -f 'hermes gateway' 2>/dev/null || true
  sleep 3
  systemctl start hermes-gateway
  sleep 2
  echo ACTIVE=\$(systemctl is-active hermes-gateway)
  echo PROC=\$(pgrep -c -u shima -f 'hermes gateway')
"
echo SHIMA_CLONE_DONE
