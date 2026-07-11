#!/bin/bash
# Fix per-VM prerequisites for the weekly script:
# 1. git safe.directory for hermes-agent repo (fixes 'dubious ownership' update failure)
# 2. ensure tg_send.py present in each user home
VMS="119:shayla:192.0.2.228 121:daisy:192.0.2.230 122:eissa:192.0.2.231 123:shima:192.0.2.232 124:travis:192.0.2.233"
for entry in $VMS; do
  id=${entry%%:*}; rest=${entry#*:}; u=${rest%%:*}; ip=${rest##*:}
  echo "=== VM $id ($u @ $ip) ==="
  scp -q -o StrictHostKeyChecking=no /root/tg_send.py root@$ip:/home/$u/tg_send.py
  ssh -o StrictHostKeyChecking=no root@$ip "
    chown $u:$u /home/$u/tg_send.py
    git config --global --add safe.directory /usr/local/lib/hermes-agent
    git config --global --add safe.directory '*'
    echo 'git safe set'; ls -l /home/$u/tg_send.py
  " 2>&1
done
echo FIX_DONE
