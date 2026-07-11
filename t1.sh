
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=15 -o PreferredAuthentications=password -o PubkeyAuthentication=no onyx@192.0.2.229 "echo SSH_OK; hostname" > /tmp/t.log 2>&1
echo "EXIT=$?" >> /tmp/t.log
