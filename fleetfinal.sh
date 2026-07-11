#!/bin/bash
# Final fleet health check (read-only).
declare -A U=( [119]=shayla [121]=daisy [122]=eissa [123]=shima [124]=travis )
for id in 119 121 122 123 124; do
  u=${U[$id]}
  ip=$(qm guest exec "$id" -- hostname -I 2>/dev/null | grep -oE "[0-9.]+" | head -1)
  echo "######## VM $id ($ip) $u ########"
  qm guest exec "$id" -- bash -c "
    echo -n 'service_active: '; systemctl is-active hermes-gateway
    echo -n 'proc_count: '; pgrep -c -u $u -f hermes
    echo -n 'telegram: '; grep -iE 'telegram connected' /home/$u/.hermes/logs/gateway.log 2>/dev/null | tail -1 | sed -E 's/.*INFO (gateway.run|.*adapter): //'
    echo -n 'swap: '; free -h | awk '/Swap/{print \$2}'
  " 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('out-data','').replace('\\\\n','\n'))" 2>/dev/null
done
echo FLEET_DONE
