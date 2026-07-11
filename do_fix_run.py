import subprocess

HOST = "192.0.2.100"
pws = {120:"onyx",121:"daisy",122:"eissa",123:"shima",124:"travis"}

# Build a host script that, for each VM, runs qm guest exec with the fix read from a host-side file
lines = ["#!/bin/bash", "set -e"]
for vmid in [120,121,122,123,124]:
    u = pws[vmid]
    # Write the guest fix script to a host file (so no nested quoting issues)
    guestfix = (
        f"H=$(openssl passwd -6 'REPLACE_WITH_YOUR_VM_PASSWORD')\n"
        f"id {u} >/dev/null 2>&1 || useradd -m -s /bin/bash {u}\n"
        f"usermod -p \"$H\" {u}\n"
        f"usermod -aG sudo {u}\n"
        f"echo '{u} ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/{u}\n"
        f"chmod 440 /etc/sudoers.d/{u}\n"
        f"echo FIXED_{u}\n"
    )
    lines.append(f"cat > /tmp/gfix_{vmid}.sh <<'GUESTEOF'\n{guestfix}GUESTEOF")
    # Run it via guest exec, passing the file content through bash -c with $(cat)
    lines.append(f"qm guest exec {vmid} -- bash -c \"$(cat /tmp/gfix_{vmid}.sh)\"")
lines.append("echo ALL_DONE")
host_script = "\n".join(lines) + "\n"
with open(r"C:\Users\shaza\Desktop\SparkSphear_App\do_fix.sh","w",newline="\n") as f:
    f.write(host_script)

r = subprocess.run(f'scp -o StrictHostKeyChecking=no "C:\\Users\\shaza\\Desktop\\SparkSphear_App\\do_fix.sh" root@{HOST}:/tmp/do_fix.sh', shell=True, capture_output=True, text=True, timeout=30)
out = subprocess.run(f'ssh -o StrictHostKeyChecking=no root@{HOST} "bash /tmp/do_fix.sh 2>&1"', shell=True, capture_output=True, text=True, timeout=120)
print(out.stdout.strip())
print("ERR:", out.stderr.strip()[:300])