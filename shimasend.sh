#!/bin/bash
# Send a test message from Shima to your Telegram to prove she works.
qm guest exec 123 -- bash -c "
  cd /home/shima
  /usr/local/lib/hermes-agent/venv/bin/hermes send -t telegram -c 7018094108 -m 'Hi Shazaly — this is Shima, your SparkSphear agent. My gateway is live and wired to Telegram. Confirm you got this and I am fully operational.' 2>&1 | tail -4
" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('out-data','').replace('\\\\n','\n'))" 2>/dev/null
echo SEND_DONE
