
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null onyx@192.0.2.229 "cd /home/onyx && timeout 90 /usr/local/lib/hermes-agent/venv/bin/hermes -z 'Say hello in two words.' 2>&1 | tail -3" > /tmp/ws.log 2>&1
cat /tmp/ws.log
