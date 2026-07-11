#!/bin/bash
set -e
PW="REPLACE_WITH_YOUR_VM_PASSWORD"
setup() {
  local user=$1 ip=$2 agent=$3
  echo "=== setup $agent ($user@$ip) ==="
  # copy needed files INTO the VM first
  sshpass -p "$PW" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /tmp/hermes.service /tmp/hermes-gateway.service /tmp/ocr_skill_pkg/ocr ${user}@${ip}:/tmp/ 2>&1 | tail -1
  sshpass -p "$PW" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${user}@${ip} bash -s <<EOF
set -e
mkdir -p ~/.hermes/skills/ocr
cp /tmp/ocr/ocr.py ~/.hermes/skills/ocr/ocr.py
cp /tmp/ocr/SKILL.md ~/.hermes/skills/ocr/SKILL.md
sed "s/__USER__/${user}/g" /tmp/hermes.service > /tmp/h.service
sed "s/__USER__/${user}/g" /tmp/hermes-gateway.service > /tmp/hg.service
sudo cp /tmp/h.service /etc/systemd/system/hermes.service
sudo cp /tmp/hg.service /etc/systemd/system/hermes-gateway.service
sudo chmod 644 /etc/systemd/system/hermes.service /etc/systemd/system/hermes-gateway.service
sudo systemctl daemon-reload
sudo systemctl enable --now hermes.service 2>&1 | tail -1
sudo systemctl enable hermes-gateway.service 2>&1 | tail -1
echo "SERVICES_${agent}"
EOF
}
setup onyx 192.0.2.229 onyx
setup daisy 192.0.2.230 daisy
setup eissa 192.0.2.231 eissa
setup shima 192.0.2.232 shima
setup travis 192.0.2.233 travis
echo "ALL_SETUP"