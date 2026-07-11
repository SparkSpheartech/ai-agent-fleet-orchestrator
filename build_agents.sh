#!/bin/bash
set -e
# === Onyx VMID 120 ===
qm create 120 --name OnyxVM --memory 4096 --cores 2 --cpu host --machine q35 --ostype l26 --net0 virtio,bridge=vmbr0 --scsihw virtio-scsi-pci --bios ovmf --efidisk0 local-lvm:0 --agent enabled=1
qm importdisk 120 /mnt/pve/Storage1/ubuntu-24.04-server-cloudimg-amd64.img local-lvm --format qcow2
qm set 120 --scsi0 local-lvm:vm-120-disk-1 --boot order=scsi0
qm set 120 --ide2 local-lvm:cloudinit --serial0 socket --vga serial0
qm set 120 --ciuser onyx --cipassword 'REPLACE_WITH_YOUR_VM_PASSWORD'
qm set 120 --ipconfig0 ip=dhcp
qm resize 120 scsi0 40G
echo I2Nsb3VkLWNvbmZpZwpwYWNrYWdlX3VwZGF0ZTogdHJ1ZQpwYWNrYWdlczoKICAtIHFlbXUtZ3Vlc3QtYWdlbnQKICAtIG5mcy1jb21tb24KcnVuY21kOgogIC0gc3lzdGVtY3RsIGVuYWJsZSAtLW5vdyBxZW11LWd1ZXN0LWFnZW50CiAgLSBzZWQgLWkgJ3MvXiMqUGFzc3dvcmRBdXRoZW50aWNhdGlvbi4qL1Bhc3N3b3JkQXV0aGVudGljYXRpb24geWVzLycgL2V0Yy9zc2gvc3NoZF9jb25maWcKICAtIHNlZCAtaSAncy9eIypLYmRJbnRlcmFjdGl2ZUF1dGhlbnRpY2F0aW9uLiovS2JkSW50ZXJhY3RpdmVBdXRoZW50aWNhdGlvbiB5ZXMvJyAvZXRjL3NzaC9zc2hkX2NvbmZpZwogIC0gZWNobyAnb255eDpTcGFya1NwaGVhcjIwMjYhJyB8IGNocGFzc3dkCiAgLSBzeXN0ZW1jdGwgcmVzdGFydCBzc2gKICAtIG1rZGlyIC1wIC9zcGFya3NwaGVhcgogIC0gZWNobyAnMTkyLjE2OC42LjEwMDovbW50L3B2ZS9zcGFya3NwaGVhcl9zaGFyZWQgL3NwYXJrc3BoZWFyIG5mcyBkZWZhdWx0cyx0aW1lbz0zMCxyZXRyeT0zIDAgMCcgPj4gL2V0Yy9mc3RhYgogIC0gbW91bnQgLWEK | base64 -d > /var/lib/vz/snippets/Onyx_ci.yaml
qm set 120 --cicustom user=local:snippets/Onyx_ci.yaml
qm start 120
# === Daisy VMID 121 ===
qm create 121 --name DaisyVM --memory 4096 --cores 2 --cpu host --machine q35 --ostype l26 --net0 virtio,bridge=vmbr0 --scsihw virtio-scsi-pci --bios ovmf --efidisk0 local-lvm:0 --agent enabled=1
qm importdisk 121 /mnt/pve/Storage1/ubuntu-24.04-server-cloudimg-amd64.img local-lvm --format qcow2
qm set 121 --scsi0 local-lvm:vm-121-disk-1 --boot order=scsi0
qm set 121 --ide2 local-lvm:cloudinit --serial0 socket --vga serial0
qm set 121 --ciuser daisy --cipassword 'REPLACE_WITH_YOUR_VM_PASSWORD'
qm set 121 --ipconfig0 ip=dhcp
qm resize 121 scsi0 40G
echo I2Nsb3VkLWNvbmZpZwpwYWNrYWdlX3VwZGF0ZTogdHJ1ZQpwYWNrYWdlczoKICAtIHFlbXUtZ3Vlc3QtYWdlbnQKICAtIG5mcy1jb21tb24KcnVuY21kOgogIC0gc3lzdGVtY3RsIGVuYWJsZSAtLW5vdyBxZW11LWd1ZXN0LWFnZW50CiAgLSBzZWQgLWkgJ3MvXiMqUGFzc3dvcmRBdXRoZW50aWNhdGlvbi4qL1Bhc3N3b3JkQXV0aGVudGljYXRpb24geWVzLycgL2V0Yy9zc2gvc3NoZF9jb25maWcKICAtIHNlZCAtaSAncy9eIypLYmRJbnRlcmFjdGl2ZUF1dGhlbnRpY2F0aW9uLiovS2JkSW50ZXJhY3RpdmVBdXRoZW50aWNhdGlvbiB5ZXMvJyAvZXRjL3NzaC9zc2hkX2NvbmZpZwogIC0gZWNobyAnZGFpc3k6U3BhcmtTcGhlYXIyMDI2IScgfCBjaHBhc3N3ZAogIC0gc3lzdGVtY3RsIHJlc3RhcnQgc3NoCiAgLSBta2RpciAtcCAvc3BhcmtzcGhlYXIKICAtIGVjaG8gJzE5Mi4xNjguNi4xMDA6L21udC9wdmUvc3BhcmtzcGhlYXJfc2hhcmVkIC9zcGFya3NwaGVhciBuZnMgZGVmYXVsdHMsdGltZW89MzAscmV0cnk9MyAwIDAnID4+IC9ldGMvZnN0YWIKICAtIG1vdW50IC1hCg== | base64 -d > /var/lib/vz/snippets/Daisy_ci.yaml
qm set 121 --cicustom user=local:snippets/Daisy_ci.yaml
qm start 121
# === Eissa VMID 122 ===
qm create 122 --name EissaVM --memory 4096 --cores 2 --cpu host --machine q35 --ostype l26 --net0 virtio,bridge=vmbr0 --scsihw virtio-scsi-pci --bios ovmf --efidisk0 local-lvm:0 --agent enabled=1
qm importdisk 122 /mnt/pve/Storage1/ubuntu-24.04-server-cloudimg-amd64.img local-lvm --format qcow2
qm set 122 --scsi0 local-lvm:vm-122-disk-1 --boot order=scsi0
qm set 122 --ide2 local-lvm:cloudinit --serial0 socket --vga serial0
qm set 122 --ciuser eissa --cipassword 'REPLACE_WITH_YOUR_VM_PASSWORD'
qm set 122 --ipconfig0 ip=dhcp
qm resize 122 scsi0 40G
echo I2Nsb3VkLWNvbmZpZwpwYWNrYWdlX3VwZGF0ZTogdHJ1ZQpwYWNrYWdlczoKICAtIHFlbXUtZ3Vlc3QtYWdlbnQKICAtIG5mcy1jb21tb24KcnVuY21kOgogIC0gc3lzdGVtY3RsIGVuYWJsZSAtLW5vdyBxZW11LWd1ZXN0LWFnZW50CiAgLSBzZWQgLWkgJ3MvXiMqUGFzc3dvcmRBdXRoZW50aWNhdGlvbi4qL1Bhc3N3b3JkQXV0aGVudGljYXRpb24geWVzLycgL2V0Yy9zc2gvc3NoZF9jb25maWcKICAtIHNlZCAtaSAncy9eIypLYmRJbnRlcmFjdGl2ZUF1dGhlbnRpY2F0aW9uLiovS2JkSW50ZXJhY3RpdmVBdXRoZW50aWNhdGlvbiB5ZXMvJyAvZXRjL3NzaC9zc2hkX2NvbmZpZwogIC0gZWNobyAnZWlzc2E6U3BhcmtTcGhlYXIyMDI2IScgfCBjaHBhc3N3ZAogIC0gc3lzdGVtY3RsIHJlc3RhcnQgc3NoCiAgLSBta2RpciAtcCAvc3BhcmtzcGhlYXIKICAtIGVjaG8gJzE5Mi4xNjguNi4xMDA6L21udC9wdmUvc3BhcmtzcGhlYXJfc2hhcmVkIC9zcGFya3NwaGVhciBuZnMgZGVmYXVsdHMsdGltZW89MzAscmV0cnk9MyAwIDAnID4+IC9ldGMvZnN0YWIKICAtIG1vdW50IC1hCg== | base64 -d > /var/lib/vz/snippets/Eissa_ci.yaml
qm set 122 --cicustom user=local:snippets/Eissa_ci.yaml
qm start 122
# === Shima VMID 123 ===
qm create 123 --name ShimaVM --memory 4096 --cores 2 --cpu host --machine q35 --ostype l26 --net0 virtio,bridge=vmbr0 --scsihw virtio-scsi-pci --bios ovmf --efidisk0 local-lvm:0 --agent enabled=1
qm importdisk 123 /mnt/pve/Storage1/ubuntu-24.04-server-cloudimg-amd64.img local-lvm --format qcow2
qm set 123 --scsi0 local-lvm:vm-123-disk-1 --boot order=scsi0
qm set 123 --ide2 local-lvm:cloudinit --serial0 socket --vga serial0
qm set 123 --ciuser shima --cipassword 'REPLACE_WITH_YOUR_VM_PASSWORD'
qm set 123 --ipconfig0 ip=dhcp
qm resize 123 scsi0 40G
echo I2Nsb3VkLWNvbmZpZwpwYWNrYWdlX3VwZGF0ZTogdHJ1ZQpwYWNrYWdlczoKICAtIHFlbXUtZ3Vlc3QtYWdlbnQKICAtIG5mcy1jb21tb24KcnVuY21kOgogIC0gc3lzdGVtY3RsIGVuYWJsZSAtLW5vdyBxZW11LWd1ZXN0LWFnZW50CiAgLSBzZWQgLWkgJ3MvXiMqUGFzc3dvcmRBdXRoZW50aWNhdGlvbi4qL1Bhc3N3b3JkQXV0aGVudGljYXRpb24geWVzLycgL2V0Yy9zc2gvc3NoZF9jb25maWcKICAtIHNlZCAtaSAncy9eIypLYmRJbnRlcmFjdGl2ZUF1dGhlbnRpY2F0aW9uLiovS2JkSW50ZXJhY3RpdmVBdXRoZW50aWNhdGlvbiB5ZXMvJyAvZXRjL3NzaC9zc2hkX2NvbmZpZwogIC0gZWNobyAnc2hpbWE6U3BhcmtTcGhlYXIyMDI2IScgfCBjaHBhc3N3ZAogIC0gc3lzdGVtY3RsIHJlc3RhcnQgc3NoCiAgLSBta2RpciAtcCAvc3BhcmtzcGhlYXIKICAtIGVjaG8gJzE5Mi4xNjguNi4xMDA6L21udC9wdmUvc3BhcmtzcGhlYXJfc2hhcmVkIC9zcGFya3NwaGVhciBuZnMgZGVmYXVsdHMsdGltZW89MzAscmV0cnk9MyAwIDAnID4+IC9ldGMvZnN0YWIKICAtIG1vdW50IC1hCg== | base64 -d > /var/lib/vz/snippets/Shima_ci.yaml
qm set 123 --cicustom user=local:snippets/Shima_ci.yaml
qm start 123
# === Travis VMID 124 ===
qm create 124 --name TravisVM --memory 4096 --cores 2 --cpu host --machine q35 --ostype l26 --net0 virtio,bridge=vmbr0 --scsihw virtio-scsi-pci --bios ovmf --efidisk0 local-lvm:0 --agent enabled=1
qm importdisk 124 /mnt/pve/Storage1/ubuntu-24.04-server-cloudimg-amd64.img local-lvm --format qcow2
qm set 124 --scsi0 local-lvm:vm-124-disk-1 --boot order=scsi0
qm set 124 --ide2 local-lvm:cloudinit --serial0 socket --vga serial0
qm set 124 --ciuser travis --cipassword 'REPLACE_WITH_YOUR_VM_PASSWORD'
qm set 124 --ipconfig0 ip=dhcp
qm resize 124 scsi0 40G
echo I2Nsb3VkLWNvbmZpZwpwYWNrYWdlX3VwZGF0ZTogdHJ1ZQpwYWNrYWdlczoKICAtIHFlbXUtZ3Vlc3QtYWdlbnQKICAtIG5mcy1jb21tb24KcnVuY21kOgogIC0gc3lzdGVtY3RsIGVuYWJsZSAtLW5vdyBxZW11LWd1ZXN0LWFnZW50CiAgLSBzZWQgLWkgJ3MvXiMqUGFzc3dvcmRBdXRoZW50aWNhdGlvbi4qL1Bhc3N3b3JkQXV0aGVudGljYXRpb24geWVzLycgL2V0Yy9zc2gvc3NoZF9jb25maWcKICAtIHNlZCAtaSAncy9eIypLYmRJbnRlcmFjdGl2ZUF1dGhlbnRpY2F0aW9uLiovS2JkSW50ZXJhY3RpdmVBdXRoZW50aWNhdGlvbiB5ZXMvJyAvZXRjL3NzaC9zc2hkX2NvbmZpZwogIC0gZWNobyAndHJhdmlzOlNwYXJrU3BoZWFyMjAyNiEnIHwgY2hwYXNzd2QKICAtIHN5c3RlbWN0bCByZXN0YXJ0IHNzaAogIC0gbWtkaXIgLXAgL3NwYXJrc3BoZWFyCiAgLSBlY2hvICcxOTIuMTY4LjYuMTAwOi9tbnQvcHZlL3NwYXJrc3BoZWFyX3NoYXJlZCAvc3BhcmtzcGhlYXIgbmZzIGRlZmF1bHRzLHRpbWVvPTMwLHJldHJ5PTMgMCAwJyA+PiAvZXRjL2ZzdGFiCiAgLSBtb3VudCAtYQo= | base64 -d > /var/lib/vz/snippets/Travis_ci.yaml
qm set 124 --cicustom user=local:snippets/Travis_ci.yaml
qm start 124
