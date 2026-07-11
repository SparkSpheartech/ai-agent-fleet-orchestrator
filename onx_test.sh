
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=20 onyx@192.0.2.229 "hostname; echo '---'; ls /sparksphear/; echo '---'; mount | grep sparksphear && echo NFS_OK || echo NFS_MISSING" > /tmp/onx_test.log 2>&1
echo "SSH_EXIT=$?" >> /tmp/onx_test.log
