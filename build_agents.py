import subprocess, base64

HOST = "192.0.2.100"

def ssh(cmd, timeout=400):
    r = subprocess.run(f'ssh -o StrictHostKeyChecking=no root@192.0.2.100 "{cmd}"',
                       shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip() + ("\n[ERR] " + r.stderr.strip() if r.stderr.strip() else "")

# Agents: name -> vmid, username
AGENTS = [
    ("Onyx",   120, "onyx"),
    ("Daisy",  121, "daisy"),
    ("Eissa",  122, "eissa"),
    ("Shima",  123, "shima"),
    ("Travis", 124, "travis"),
]
PW = "REPLACE_WITH_YOUR_VM_PASSWORD"
IMG = "/mnt/pve/Storage1/ubuntu-24.04-server-cloudimg-amd64.img"
HOST_IP = "192.0.2.100"
NFS = f"{HOST_IP}:/mnt/pve/sparksphear_shared"

# cloud-init snippet (per agent) -> sets pw auth, guest agent, nfs mount
def ci_snippet(user):
    return f"""#cloud-config
package_update: true
packages:
  - qemu-guest-agent
  - nfs-common
runcmd:
  - systemctl enable --now qemu-guest-agent
  - sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
  - sed -i 's/^#*KbdInteractiveAuthentication.*/KbdInteractiveAuthentication yes/' /etc/ssh/sshd_config
  - echo '{user}:{PW}' | chpasswd
  - systemctl restart ssh
  - mkdir -p /sparksphear
  - echo '{NFS} /sparksphear nfs defaults,timeo=30,retry=3 0 0' >> /etc/fstab
  - mount -a
"""

# Build the host script that creates all 5 VMs
lines = ["#!/bin/bash", "set -e"]
for name, vmid, user in AGENTS:
    snip_b64 = base64.b64encode(ci_snippet(user).encode()).decode()
    lines.append(f"# === {name} VMID {vmid} ===")
    lines.append(f"qm create {vmid} --name {name}VM --memory 4096 --cores 2 --cpu host --machine q35 --ostype l26 --net0 virtio,bridge=vmbr0 --scsihw virtio-scsi-pci --bios ovmf --efidisk0 local-lvm:0 --agent enabled=1")
    lines.append(f"qm importdisk {vmid} {IMG} local-lvm --format qcow2")
    lines.append(f"qm set {vmid} --scsi0 local-lvm:vm-{vmid}-disk-1 --boot order=scsi0")
    lines.append(f"qm set {vmid} --ide2 local-lvm:cloudinit --serial0 socket --vga serial0")
    lines.append(f"qm set {vmid} --ciuser {user} --cipassword '{PW}'")
    lines.append(f"qm set {vmid} --ipconfig0 ip=dhcp")
    lines.append(f"qm resize {vmid} scsi0 40G")
    lines.append(f"echo {snip_b64} | base64 -d > /var/lib/vz/snippets/{name}_ci.yaml")
    lines.append(f"qm set {vmid} --cicustom user=local:snippets/{name}_ci.yaml")
    lines.append(f"qm start {vmid}")

host_script = "\n".join(lines) + "\n"

# Write host script via base64 to avoid quoting issues
hb64 = base64.b64encode(host_script.encode()).decode()
print(ssh(f"echo {hb64} | base64 -d > /tmp/build_agents.sh && echo WRITTEN && wc -l /tmp/build_agents.sh"))