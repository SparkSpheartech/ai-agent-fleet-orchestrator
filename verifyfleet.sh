#!/bin/bash
declare -A U=( [119]=shayla [120]=onyx [121]=daisy [122]=eissa [123]=shima [124]=travis )
for id in 119 120 121 122 123 124; do
  u=${U[$id]}
  echo "######## VM $id ($u) ########"
  qm guest exec "$id" -- bash -c "
    echo active=\$(systemctl is-active hermes-gateway)
    H=/home/$u
    L=\$H/.hermes/logs/gateway.log
    echo -n 'telegram_line: '
    grep -iE 'telegram connected|polling conflict|terminated by other' \"\$L\" 2>/dev/null | tail -1
    echo -n 'proc_count: '
    pgrep -c -u $u -f 'hermes gateway'
  " 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('out-data','').replace('\\\\n','\n'))" 2>/dev/null
done
echo "VERIFY DONE"
