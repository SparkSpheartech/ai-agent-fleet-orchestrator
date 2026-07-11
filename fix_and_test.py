import subprocess

HOST = "192.0.2.100"
pws = {120:"onyx",121:"daisy",122:"eissa",123:"shima",124:"travis"}
vips = {120:"192.0.2.229",121:"192.0.2.230",122:"192.0.2.231",123:"192.0.2.232",124:"192.0.2.233"}

lines = ["#!/bin/bash"]
for vmid in [120,121,122,123,124]:
    u = pws[vmid]; v = vips[vmid]
    # On host: copy pubkey? No - use password. Just test + fix sudo via guest exec per VM
    lines.append(f"echo '=== VM{vmid} {u} ==='")
    # ensure sudoers via guest exec (openssl pw already set for 120; do all)
    lines.append(f'sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=15 {u}@{v} "echo SUDO_TEST; sudo -n true && echo SUDO_OK || echo SUDO_NEEDS_PW"')
host_script = "\n".join(lines) + "\n"
with open(r"C:\Users\shaza\Desktop\SparkSphear_App\test_sudo.sh","w",newline="\n") as f:
    f.write(host_script)

# Fix sudo + ensure pw for 121-124 via guest exec (openssl method), per VM
for vmid in [121,122,123,124]:
    u = pws[vmid]
    fix = (f"H=$(openssl passwd -6 'REPLACE_WITH_YOUR_VM_PASSWORD'); "
           f"id {u} >/dev/null 2>&1 || useradd -m -s /bin/bash {u}; "
           f"usermod -p \"$H\" {u}; usermod -aG sudo {u}; "
           f"echo '{u} ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/{u}; chmod 440 /etc/sudoers.d/{u}; "
           f"echo DONE_{u}")
    r = subprocess.run(f'ssh -o StrictHostKeyChecking=no root@{HOST} "qm guest exec {vmid} -- bash -c \'{fix}\'"', shell=True, capture_output=True, text=True, timeout=60)
    print(f"VM{vmid} ({u}) fix:", r.stdout.strip()[:80], r.stderr.strip()[:80])

# Also fix VM120 sudoers (was missed)
r = subprocess.run(f'ssh -o StrictHostKeyChecking=no root@{HOST} "qm guest exec 120 -- bash -c \'echo \"onyx ALL=(ALL) NOPASSWD:ALL\" > /etc/sudoers.d/onyx; chmod 440 /etc/sudoers.d/onyx; echo OK\'"', shell=True, capture_output=True, text=True, timeout=60)
print("VM120 sudoers:", r.stdout.strip()[:80])

# Run sudo test
r2 = subprocess.run(f'scp -o StrictHostKeyChecking=no "C:\\Users\\shaza\\Desktop\\SparkSphear_App\\test_sudo.sh" root@{HOST}:/tmp/test_sudo.sh', shell=True, capture_output=True, text=True, timeout=30)
out = subprocess.run(f'ssh -o StrictHostKeyChecking=no root@{HOST} "bash /tmp/test_sudo.sh"', shell=True, capture_output=True, text=True, timeout=120)
print(out.stdout.strip())
print("ERR:", out.stderr.strip()[:200])