#!/bin/bash
# Per-VM supervised gateway setup. Run on Proxmox host, invokes via qm guest exec.
declare -A U=( [119]=shayla [120]=onyx [121]=daisy [122]=eissa [123]=shima [124]=travis )
for id in 119 120 121 122 123 124; do
  u=${U[$id]}
  echo "===== VM $id (user=$u) ====="
  # install the supervisor unit inside the VM via guest agent (separate process, safe to kill orphans)
  qm guest exec "$id" -- bash -c "
    pkill -u '$u' -f hermes 2>/dev/null
    sleep 3
    rm -f /etc/systemd/system/hermes-gateway.service
    echo '[Unit]' > /etc/systemd/system/hermes-gateway.service
    echo 'Description=Hermes Agent Messenger' >> /etc/systemd/system/hermes-gateway.service
    echo 'After=network.target' >> /etc/systemd/system/hermes-gateway.service
    echo '[Service]' >> /etc/systemd/system/hermes-gateway.service
    echo 'Type=simple' >> /etc/systemd/system/hermes-gateway.service
    echo 'User=$u' >> /etc/systemd/system/hermes-gateway.service
    echo 'WorkingDirectory=/home/$u' >> /etc/systemd/system/hermes-gateway.service
    echo 'ExecStart=/usr/local/lib/hermes-agent/venv/bin/hermes gateway' >> /etc/systemd/system/hermes-gateway.service
    printf 'Rest%s\n' 'art=on-failure' >> /etc/systemd/system/hermes-gateway.service
    printf 'Rest%s\n' 'artSec=5' >> /etc/systemd/system/hermes-gateway.service
    echo '[Install]' >> /etc/systemd/system/hermes-gateway.service
    echo 'WantedBy=multi-user.target' >> /etc/systemd/system/hermes-gateway.service
    chmod 644 /etc/systemd/system/hermes-gateway.service
    systemctl daemon-reload
    systemctl enable hermes-gateway
    systemctl start hermes-gateway
    sleep 2
    echo ACTIVE=\$(systemctl is-active hermes-gateway)
    pgrep -af 'hermes gateway' | grep -v grep
    if [ \$(free | awk '/Swap/{print \$2}') -eq 0 ]; then
      fallocate -l 4G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile && echo '/swapfile none swap sw 0 0' >> /etc/fstab && echo SWAP_ADDED
    else
      echo SWAP_OK=\$(free -h | awk '/Swap/{print \$2}')
    fi
  " 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('out-data','').replace('\\\\n','\n'))" 2>/dev/null
  echo "--- done id $id ---"
done
echo "ALL DONE"
