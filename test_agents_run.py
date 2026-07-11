import subprocess

HOST = "192.0.2.100"
vms = {"onyx":("120","192.0.2.229"),"daisy":("121","192.0.2.230"),
       "eissa":("122","192.0.2.231"),"shima":("123","192.0.2.232"),"travis":("124","192.0.2.233")}
lines = ["#!/bin/bash"]
for agent,(vmid,ip) in vms.items():
    lines.append(f"echo '=== {agent} ({ip}) ==='")
    lines.append(f'sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {agent}@{ip} "cd ~/ && timeout 60 /usr/local/lib/hermes-agent/venv/bin/hermes -z \'say hi in 3 words\' 2>&1 | tail -3"')
host_script = "\n".join(lines) + "\n"
with open(r"C:\Users\shaza\Desktop\SparkSphear_App\test_agents.sh","w",newline="\n") as f:
    f.write(host_script)
r = subprocess.run(f'scp -o StrictHostKeyChecking=no "C:\\Users\\shaza\\Desktop\\SparkSphear_App\\test_agents.sh" root@{HOST}:/tmp/test_agents.sh', shell=True, capture_output=True, text=True, timeout=30)
out = subprocess.run(f'ssh -o StrictHostKeyChecking=no root@{HOST} "bash /tmp/test_agents.sh 2>&1"', shell=True, capture_output=True, text=True, timeout=200)
print(out.stdout.strip())
print("ERR:", out.stderr.strip()[:200])