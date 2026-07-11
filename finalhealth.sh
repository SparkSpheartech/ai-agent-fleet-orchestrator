#!/bin/bash
echo "=== cron ==="; crontab -l
echo "=== fleet health ==="
for ip in 192.0.2.228 192.0.2.230 192.0.2.231 192.0.2.232 192.0.2.233; do
  ssh -o StrictHostKeyChecking=no root@$ip 'u=$(ls -d /home/*|head -1|cut -d/ -f3); printf "%s %s: active=%s proc=%s tg=%s\n" "$1" "$u" "$(systemctl is-active hermes-gateway)" "$(pgrep -c -u $u -f hermes)" "$(grep -c "telegram connected" /home/$u/.hermes/logs/gateway.log)"' 2>&1 _ $ip
done
echo "=== my session ==="; echo "host check done"
