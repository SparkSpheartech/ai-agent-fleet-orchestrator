#!/bin/bash
set -e
echo "=== copy to VM120 onyx ==="
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r /tmp/hermes-agent onyx@192.0.2.229:/usr/local/lib/hermes-agent 2>&1 | tail -1
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null onyx@192.0.2.229 "chmod +x /usr/local/lib/hermes-agent/venv/bin/hermes; ln -sf /usr/local/lib/hermes-agent/venv/bin/hermes /usr/local/bin/hermes; /usr/local/lib/hermes-agent/venv/bin/hermes --version" 2>&1 | tail -2
echo "=== copy to VM121 daisy ==="
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r /tmp/hermes-agent daisy@192.0.2.230:/usr/local/lib/hermes-agent 2>&1 | tail -1
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null daisy@192.0.2.230 "chmod +x /usr/local/lib/hermes-agent/venv/bin/hermes; ln -sf /usr/local/lib/hermes-agent/venv/bin/hermes /usr/local/bin/hermes; /usr/local/lib/hermes-agent/venv/bin/hermes --version" 2>&1 | tail -2
echo "=== copy to VM122 eissa ==="
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r /tmp/hermes-agent eissa@192.0.2.231:/usr/local/lib/hermes-agent 2>&1 | tail -1
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null eissa@192.0.2.231 "chmod +x /usr/local/lib/hermes-agent/venv/bin/hermes; ln -sf /usr/local/lib/hermes-agent/venv/bin/hermes /usr/local/bin/hermes; /usr/local/lib/hermes-agent/venv/bin/hermes --version" 2>&1 | tail -2
echo "=== copy to VM123 shima ==="
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r /tmp/hermes-agent shima@192.0.2.232:/usr/local/lib/hermes-agent 2>&1 | tail -1
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null shima@192.0.2.232 "chmod +x /usr/local/lib/hermes-agent/venv/bin/hermes; ln -sf /usr/local/lib/hermes-agent/venv/bin/hermes /usr/local/bin/hermes; /usr/local/lib/hermes-agent/venv/bin/hermes --version" 2>&1 | tail -2
echo "=== copy to VM124 travis ==="
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r /tmp/hermes-agent travis@192.0.2.233:/usr/local/lib/hermes-agent 2>&1 | tail -1
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null travis@192.0.2.233 "chmod +x /usr/local/lib/hermes-agent/venv/bin/hermes; ln -sf /usr/local/lib/hermes-agent/venv/bin/hermes /usr/local/bin/hermes; /usr/local/lib/hermes-agent/venv/bin/hermes --version" 2>&1 | tail -2
echo "ALL_HERMES_PUSHED"