
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null shayla@192.0.2.228 "echo WHICH=$(which hermes); echo REAL=$(readlink -f $(which hermes)); echo ---; ls /usr/local/lib/hermes-agent 2>/dev/null | head; echo ---SERVICE---; cat /etc/systemd/system/hermes-agent.service 2>/dev/null" > /tmp/shayla_probe.log 2>&1
cat /tmp/shayla_probe.log
