#!/bin/bash
push() {
  local vmid=$1 user=$2 ip=$3
  echo "=== copy to VM$vmid $user ==="
  tar czf - -C /tmp hermes-agent | sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${user}@${ip} "sudo tar xzf - -C /usr/local/lib" 2>&1 | tail -1
  sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${user}@${ip} "sudo chmod +x /usr/local/lib/hermes-agent/venv/bin/hermes; sudo ln -sf /usr/local/lib/hermes-agent/venv/bin/hermes /usr/local/bin/hermes; /usr/local/lib/hermes-agent/venv/bin/hermes --version" 2>&1 | tail -2
}
push 120 onyx 192.0.2.229
push 121 daisy 192.0.2.230
push 122 eissa 192.0.2.231
push 123 shima 192.0.2.232
push 124 travis 192.0.2.233
echo "ALL_HERMES_PUSHED"