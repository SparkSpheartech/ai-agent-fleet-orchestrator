#!/bin/bash
echo '=== onyx (192.0.2.229) ==='
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null onyx@192.0.2.229 "cd ~/ && timeout 60 /usr/local/lib/hermes-agent/venv/bin/hermes -z 'say hi in 3 words' 2>&1 | tail -3"
echo '=== daisy (192.0.2.230) ==='
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null daisy@192.0.2.230 "cd ~/ && timeout 60 /usr/local/lib/hermes-agent/venv/bin/hermes -z 'say hi in 3 words' 2>&1 | tail -3"
echo '=== eissa (192.0.2.231) ==='
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null eissa@192.0.2.231 "cd ~/ && timeout 60 /usr/local/lib/hermes-agent/venv/bin/hermes -z 'say hi in 3 words' 2>&1 | tail -3"
echo '=== shima (192.0.2.232) ==='
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null shima@192.0.2.232 "cd ~/ && timeout 60 /usr/local/lib/hermes-agent/venv/bin/hermes -z 'say hi in 3 words' 2>&1 | tail -3"
echo '=== travis (192.0.2.233) ==='
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null travis@192.0.2.233 "cd ~/ && timeout 60 /usr/local/lib/hermes-agent/venv/bin/hermes -z 'say hi in 3 words' 2>&1 | tail -3"
