
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=15 onyx@192.0.2.229 "echo CONNECTED_AS=$(whoami); hostname; ls -la /sparksphear/ 2>&1 | head -5; mount | grep sparksphear && echo NFS_OK || echo NFS_MISSING" 2>&1
echo "EXIT=$?"
