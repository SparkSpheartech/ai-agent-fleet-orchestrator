
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=15 onyx@192.0.2.229 "echo SSH_OK; hostname; mount | grep -q sparksphear && echo NFS_OK || echo NFS_MISSING" > /tmp/v120.log 2>&1
echo "EXIT=$?" >> /tmp/v120.log
cat /tmp/v120.log
