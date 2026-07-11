#!/bin/bash
# Settle systemd unit state on agent VMs (reset-failed + ensure clean active).
VMS="119:shayla:192.0.2.228 121:daisy:192.0.2.230 122:eissa:192.0.2.231 123:shima:192.0.2.232 124:travis:192.0.2.233"
for entry in $VMS; do
  id=${entry%%:*}; rest=${entry#*:}; u=${rest%%:*}; ip=${rest##*:}
  echo "=== VM $id ($u) ==="
  qm guest exec "$id" -- bash -c "
    systemctl reset-failed hermes-gateway 2>/dev/null
    # if still not active, let systemd respawn cleanly
    if [ \$(systemctl is-active hermes-gateway) != 'active' ]; then
      pkill -9 -u $u -f 'hermes gateway' 2>/dev/null; sleep 2
      systemctl start hermes-gateway 2>/dev/null
      sleep 6
    fi
    echo FINAL_ACTIVE=\$(systemctl is-active hermes-gateway)
    echo FINAL_PROC=\$(pgrep -c -u $u -f hermes)
    echo TG=\$(grep -c 'telegram connected' /home/$u/.hermes/logs/gateway.log)
  " 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('out-data','').replace('\\\\n','\n'))" 2>/dev/null
done
echo SETTLE_DONE
