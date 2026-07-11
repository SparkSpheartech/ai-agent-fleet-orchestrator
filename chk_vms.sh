#!/bin/bash
echo '--- VM 120 (onyx) ---'
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no onyx@192.0.2.229 "echo user=$(whoami); hostname; echo MOUNT:; ls /sparksphear/ 2>&1 | head -3; mount | grep -q sparksphear && echo NFS_OK || echo NFS_MISSING"
echo '--- VM 121 (daisy) ---'
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no daisy@192.0.2.230 "echo user=$(whoami); hostname; echo MOUNT:; ls /sparksphear/ 2>&1 | head -3; mount | grep -q sparksphear && echo NFS_OK || echo NFS_MISSING"
echo '--- VM 122 (eissa) ---'
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no eissa@192.0.2.231 "echo user=$(whoami); hostname; echo MOUNT:; ls /sparksphear/ 2>&1 | head -3; mount | grep -q sparksphear && echo NFS_OK || echo NFS_MISSING"
echo '--- VM 123 (shima) ---'
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no shima@192.0.2.232 "echo user=$(whoami); hostname; echo MOUNT:; ls /sparksphear/ 2>&1 | head -3; mount | grep -q sparksphear && echo NFS_OK || echo NFS_MISSING"
echo '--- VM 124 (travis) ---'
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no travis@192.0.2.233 "echo user=$(whoami); hostname; echo MOUNT:; ls /sparksphear/ 2>&1 | head -3; mount | grep -q sparksphear && echo NFS_OK || echo NFS_MISSING"
