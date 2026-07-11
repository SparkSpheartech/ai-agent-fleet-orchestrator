#!/bin/bash
# Repair broken hermes venv binaries on all agent VMs (caused by root-run update).
# For each: reinstall -e as the user, clean bad dist-info, start gateway.
VMS="119:shayla:192.0.2.228 121:daisy:192.0.2.230 122:eissa:192.0.2.231 123:shima:192.0.2.232 124:travis:192.0.2.233"
for entry in $VMS; do
  id=${entry%%:*}; rest=${entry#*:}; u=${rest%%:*}; ip=${rest##*:}
  echo "=== VM $id ($u) ==="
  qm guest exec "$id" -- bash -c "
    cd /usr/local/lib/hermes-agent
    su - $u -c \"cd /usr/local/lib/hermes-agent && /usr/local/lib/hermes-agent/venv/bin/pip3 install -e . --no-deps --quiet 2>&1 | tail -3\"
    rm -rf /usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/~ermes_agent-*.dist-info 2>/dev/null
    ls -la /usr/local/lib/hermes-agent/venv/bin/hermes
    /usr/local/lib/hermes-agent/venv/bin/hermes --version 2>&1 | head -1
    service hermes-gateway start 2>&1
    sleep 6
    echo ACTIVE=\$(systemctl is-active hermes-gateway)
    echo PROC=\$(pgrep -c -u $u -f hermes)
    echo TG=\$(grep -c 'telegram connected' /home/$u/.hermes/logs/gateway.log)
  " 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('out-data','').replace('\\\\n','\n'))" 2>/dev/null
done
echo REPAIR_DONE
