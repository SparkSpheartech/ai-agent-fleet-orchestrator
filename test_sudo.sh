#!/bin/bash
echo '=== VM120 onyx ==='
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=15 onyx@192.0.2.229 "echo SUDO_TEST; sudo -n true && echo SUDO_OK || echo SUDO_NEEDS_PW"
echo '=== VM121 daisy ==='
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=15 daisy@192.0.2.230 "echo SUDO_TEST; sudo -n true && echo SUDO_OK || echo SUDO_NEEDS_PW"
echo '=== VM122 eissa ==='
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=15 eissa@192.0.2.231 "echo SUDO_TEST; sudo -n true && echo SUDO_OK || echo SUDO_NEEDS_PW"
echo '=== VM123 shima ==='
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=15 shima@192.0.2.232 "echo SUDO_TEST; sudo -n true && echo SUDO_OK || echo SUDO_NEEDS_PW"
echo '=== VM124 travis ==='
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=15 travis@192.0.2.233 "echo SUDO_TEST; sudo -n true && echo SUDO_OK || echo SUDO_NEEDS_PW"
