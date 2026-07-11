#!/bin/bash
echo '=== VM 120 onyx ==='
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null onyx@192.0.2.229 "hostname; ls /sparksphear/ ; mount | grep sparksphear || echo NFS_MISSING"
echo '=== VM 121 daisy ==='
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null daisy@192.0.2.230 "hostname; ls /sparksphear/ ; mount | grep sparksphear || echo NFS_MISSING"
echo '=== VM 122 eissa ==='
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null eissa@192.0.2.231 "hostname; ls /sparksphear/ ; mount | grep sparksphear || echo NFS_MISSING"
echo '=== VM 123 shima ==='
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null shima@192.0.2.232 "hostname; ls /sparksphear/ ; mount | grep sparksphear || echo NFS_MISSING"
echo '=== VM 124 travis ==='
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null travis@192.0.2.233 "hostname; ls /sparksphear/ ; mount | grep sparksphear || echo NFS_MISSING"
