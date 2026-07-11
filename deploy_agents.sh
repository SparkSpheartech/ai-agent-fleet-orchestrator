#!/bin/bash
set -e
PW="REPLACE_WITH_YOUR_VM_PASSWORD"
deploy() {
  local user=$1 ip=$2 agent=$3
  echo "=== deploy $agent ($user@$ip) ==="
  sshpass -p "$PW" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${user}@${ip} bash -s <<EOF
set -e
mkdir -p ~/.hermes/skills
# credentials (provider + openrouter key)
cp /tmp/creds/config.yaml ~/.hermes/config.yaml
cp /tmp/creds/auth.json ~/.hermes/auth.json
cp /tmp/creds/.env ~/.hermes/.env
# persona
cp /tmp/personas/${agent}_SOUL.md ~/.hermes/SOUL.md
cp /tmp/personas/${agent}_USER.md ~/.hermes/USER.md
# web search backend
grep -q "search_backend" ~/.hermes/config.yaml || echo "search_backend: duckduckgo" >> ~/.hermes/config.yaml
# mailbox convenience symlink in home
ln -sfn /sparksphear/_agent_mailbox ~/agent_mailbox
echo "DEPLOYED_${agent}"
EOF
}
deploy onyx 192.0.2.229 onyx
deploy daisy 192.0.2.230 daisy
deploy eissa 192.0.2.231 eissa
deploy shima 192.0.2.232 shima
deploy travis 192.0.2.233 travis
echo "ALL_DEPLOYED"