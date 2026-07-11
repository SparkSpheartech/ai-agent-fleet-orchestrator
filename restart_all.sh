#!/bin/bash
# Emergency: restart all agent gateways cleanly via guest agent.
VMS="119:shayla:192.0.2.228 121:daisy:192.0.2.230 122:eissa:192.0.2.231 123:shima:192.0.2.232 124:travis:192.0.2.233"
for entry in $VMS; do
  id=${entry%%:*}; rest=${entry#*:}; u=${rest%%:*}; ip=${rest##*:}
  echo "=== VM $id ($u) ==="
  qm guest exec "$id" -- bash -c "
    rm -f /home/$u/.hermes/kanban/.dispatcher.lock 2>/dev/null
    pkill -9 -u $u -f 'hermes gateway' 2>/dev/null; sleep 2
    systemctl start hermes-gateway
    sleep 8
    echo ACTIVE=\$(systemctl is-active hermes-gateway)
    echo PROC=\$(pgrep -c -u $u -f hermes)
    tail -1 /home/$u/.hermes/logs/gateway.log | grep -i telegram
  " 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('out-data','').replace('\\\\n','\n'))" 2>/dev/null
done
echo RESTART_DONE
