#!/bin/bash
# Fix Shima: strip control chars from config, kill stale gateway lock, restart.
SHIMAIP=192.0.2.232
# pull Daisy's config cleanly (strip control chars), push to Shima
qm guest exec 121 -- bash -c "cat /home/daisy/.hermes/config.yaml" 2>/dev/null | python3 -c "
import sys,json
d=json.load(sys.stdin)
t=d.get('out-data','')
t=t.replace('\\\\r\\\\n','\n').replace('\\\\r','\n')
# strip non-printable control chars except newline/tab
import re
t=re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]','',t)
open('/root/shima_clean.yaml','w').write(t)
print('clean bytes',len(t))
"
# also strip control chars from Shima's current .env just in case, rebuild from daisy
qm guest exec 121 -- bash -c "grep -vE '^TELEGRAM_BOT_TOKEN=|^TELEGRAM_ALLOWED_USERS=|^TELEGRAM_HOME_CHANNEL=|^TELEGRAM_HOME_CHANNEL_NAME=' /home/daisy/.hermes/.env" 2>/dev/null | python3 -c "
import sys,json,re
t=json.load(sys.stdin).get('out-data','').replace('\\\\r\\\\n','\n')
t=re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]','',t)
t+='TELEGRAM_BOT_TOKEN=8813962270:AAGnzgGQTXRe_JGr9k7YyNfc7AQHgPqxsRo\n'
t+='TELEGRAM_ALLOWED_USERS=7018094108\n'
t+='TELEGRAM_HOME_CHANNEL=7018094108\n'
t+='TELEGRAM_HOME_CHANNEL_NAME=Shazaly\n'
open('/root/shima_env.env','w').write(t)
print('env bytes',len(t))
"
# kill stale gateway lock/process on Shima, push clean files
ssh -o StrictHostKeyChecking=no root@$SHIMAIP "rm -f /home/shima/.hermes/kanban/.dispatcher.lock /home/shima/.hermes/gateway.lock 2>/dev/null; pkill -9 -u shima -f hermes 2>/dev/null; pkill -9 -f 'hermes gateway' 2>/dev/null; sleep 2; echo KILLED"
scp -q -o StrictHostKeyChecking=no /root/shima_clean.yaml root@$SHIMAIP:/home/shima/.hermes/config.yaml
scp -q -o StrictHostKeyChecking=no /root/shima_env.env root@$SHIMAIP:/home/shima/.hermes/.env
ssh -o StrictHostKeyChecking=no root@$SHIMAIP "chown shima:shima /home/shima/.hermes/config.yaml /home/shima/.hermes/.env; echo COPIED"
# verify config parses
ssh -o StrictHostKeyChecking=no root@$SHIMAIP "cd /home/shima && /usr/local/lib/hermes-agent/venv/bin/python -c \"import yaml; d=yaml.safe_load(open('.hermes/config.yaml')); print('PARSE_OK platforms:', list(d.get('platforms',{}).keys()))\""
echo SHIMA_CLEAN_DONE
