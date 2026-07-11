import subprocess

HOST = "192.0.2.100"
vms = {120:"onyx",121:"daisy",122:"eissa",123:"shima",124:"travis"}
vips = {120:"192.0.2.229",121:"192.0.2.230",122:"192.0.2.231",123:"192.0.2.232",124:"192.0.2.233"}

lines = ["#!/bin/bash"]
for vmid in [120,121,122,123,124]:
    u = vms[vmid]; v = vips[vmid]
    # Copy hermes-agent dir from host to VM
    lines.append(f"echo '=== copy to VM{vmid} {u} ==='")
    lines.append(f'sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r /tmp/hermes-agent {u}@{v}:/usr/local/lib/hermes-agent 2>&1 | tail -1')
    # Fix venv shebang (already absolute, but ensure)
    lines.append(f'sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {u}@{v} "chmod +x /usr/local/lib/hermes-agent/venv/bin/hermes; ln -sf /usr/local/lib/hermes-agent/venv/bin/hermes /usr/local/bin/hermes; /usr/local/lib/hermes-agent/venv/bin/hermes --version" 2>&1 | tail -2')
host_script = "\n".join(lines) + "\n"
with open(r"C:\Users\shaza\Desktop\SparkSphear_App\push_hermes.sh","w",newline="\n") as f:
    f.write(host_script)

r = subprocess.run(f'scp -o StrictHostKeyChecking=no "C:\\Users\\shaza\\Desktop\\SparkSphear_App\\push_hermes.sh" root@{HOST}:/tmp/push_hermes.sh', shell=True, capture_output=True, text=True, timeout=30)
out = subprocess.run(f'ssh -o StrictHostKeyChecking=no root@{HOST} "nohup bash /tmp/push_hermes.sh >/tmp/pushhermes.log 2>&1 & echo STARTED_PID=$!"', shell=True, capture_output=True, text=True, timeout=30)
print("launched:", out.stdout.strip())