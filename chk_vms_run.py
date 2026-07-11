import subprocess, base64

HOST = "192.0.2.100"
PWS = {120:"onyx",121:"daisy",122:"eissa",123:"shima",124:"travis"}
VMIPS = {120:"192.0.2.229",121:"192.0.2.230",122:"192.0.2.231",123:"192.0.2.232",124:"192.0.2.233"}

lines = ["#!/bin/bash"]
for vmid in [120,121,122,123,124]:
    user = PWS[vmid]; vip = VMIPS[vmid]
    lines.append(f"echo '--- VM {vmid} ({user}) ---'")
    lines.append(f'sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no {user}@{vip} "echo user=$(whoami); hostname; echo MOUNT:; ls /sparksphear/ 2>&1 | head -3; mount | grep -q sparksphear && echo NFS_OK || echo NFS_MISSING"')
host_script = "\n".join(lines) + "\n"
with open(r"C:\Users\shaza\Desktop\SparkSphear_App\chk_vms.sh","w",newline="\n") as f:
    f.write(host_script)
r = subprocess.run(f'scp -o StrictHostKeyChecking=no "C:\\Users\\shaza\\Desktop\\SparkSphear_App\\chk_vms.sh" root@{HOST}:/tmp/chk_vms.sh',
                   shell=True, capture_output=True, text=True, timeout=60)
print("scp:", r.stderr.strip()[:80])
print("Running...")
out = subprocess.run(f'ssh -o StrictHostKeyChecking=no root@192.0.2.100 "bash /tmp/chk_vms.sh 2>&1"',
                      shell=True, capture_output=True, text=True, timeout=120)
print(out.stdout.strip())
print("ERR:", out.stderr.strip()[:300])