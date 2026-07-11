#!/bin/bash
# Wire Shima's Telegram token into VM 123 and restart her gateway cleanly.
TOKEN="8813962270:AAGnzgGQTXRe_JGr9k7YyNfc7AQHgPqxsRo"
H=/home/shima
ENV=$H/.hermes/.env
qm guest exec 123 -- bash -c "
  set -e
  cd $H/.hermes
  # remove any existing telegram token lines
  sed -i '/^TELEGRAM_BOT_TOKEN=/d; /^TELEGRAM_ALLOWED_USERS=/d; /^TELEGRAM_HOME_CHANNEL=/d; /^TELEGRAM_HOME_CHANNEL_NAME=/d' .env
  # append shima's token block
  printf 'TELEGRAM_BOT_TOKEN=%s\n' '$TOKEN' >> .env
  printf 'TELEGRAM_ALLOWED_USERS=7018094108\n' >> .env
  printf 'TELEGRAM_HOME_CHANNEL=7018094108\n' >> .env
  printf 'TELEGRAM_HOME_CHANNEL_NAME=Shazaly\n' >> .env
  chown shima:shima .env
  echo TOKEN_WRITTEN
  # restart gateway (pkill + systemd start, not restart verb)
  pkill -u shima -f 'hermes gateway' 2>/dev/null || true
  sleep 3
  systemctl start hermes-gateway
  sleep 2
  echo ACTIVE=\$(systemctl is-active hermes-gateway)
  echo PROC=\$(pgrep -c -u shima -f 'hermes gateway')
" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('out-data','').replace('\\\\n','\n'))" 2>/dev/null
echo SHIMA_DONE
