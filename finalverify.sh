#!/bin/bash
declare -A U=( [119]=shayla [120]=onyx [121]=daisy [122]=eissa [123]=shima [124]=travis )
for id in 119 120 121 122 123 124; do
  u=${U[$id]}
  echo "######## VM $id ($u) ########"
  qm guest exec "$id" -- bash -c "
    echo -n 'service_active: '; systemctl is-active hermes-gateway
    echo -n 'proc_count: '; pgrep -c -u $u -f 'hermes gateway'
    L=/home/$u/.hermes/logs/gateway.log
    echo -n 'telegram_state: '; grep -iE 'telegram connected|polling conflict' \"\$L\" 2>/dev/null | tail -1 | sed -E 's/.*INFO (gateway.run|hermes_plugins.*adapter): //'
  " 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('out-data','').replace('\\\\n','\n'))" 2>/dev/null
done
echo FLEET_DONE
