
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null shayla@192.0.2.228 "echo '=== hermes.service ==='; sudo cat /etc/systemd/system/hermes.service; echo '=== hermes-gateway.service ==='; sudo cat /etc/systemd/system/hermes-gateway.service; echo '=== user gateway ==='; ls ~/.config/systemd/user/ 2>/dev/null" > /tmp/svc_files.log 2>&1
cat /tmp/svc_files.log
