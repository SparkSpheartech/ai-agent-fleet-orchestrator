#!/bin/bash
echo '=== VM120 onyx ==='
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null onyx@192.0.2.229 "hostname; ls /sparksphear/ | head -3; mount | grep -q sparksphear && echo NFS_OK || echo NFS_MISSING"
echo '=== VM121 daisy ==='
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null daisy@192.0.2.230 "hostname; ls /sparksphear/ | head -3; mount | grep -q sparksphear && echo NFS_OK || echo NFS_MISSING"
echo '=== VM122 eissa ==='
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null eissa@192.0.2.231 "hostname; ls /sparksphear/ | head -3; mount | grep -q sparksphear && echo NFS_OK || echo NFS_MISSING"
echo '=== VM123 shima ==='
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null shima@192.0.2.232 "hostname; ls /sparksphear/ | head -3; mount | grep -q sparksphear && echo NFS_OK || echo NFS_MISSING"
echo '=== VM124 travis ==='
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null travis@192.0.2.233 "hostname; ls /sparksphear/ | head -3; mount | grep -q sparksphear && echo NFS_OK || echo NFS_MISSING"
