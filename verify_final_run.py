import subprocess

HOST = "192.0.2.100"
vms = {"onyx":("120","192.0.2.229"),"daisy":("121","192.0.2.230"),
       "eissa":("122","192.0.2.231"),"shima":("123","192.0.2.232"),"travis":("124","192.0.2.233")}
lines = ["#!/bin/bash"]
for agent,(vmid,ip) in vms.items():
    lines.append(f"echo '=== {agent} ({ip}) ==='")
    lines.append(f'sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {agent}@{ip} "'
                 f'echo HERMES_SVC=$(systemctl is-active hermes.service); '
                 f'echo GW_SVC=$(systemctl is-active hermes-gateway.service); '
                 f'echo SOUL=$(test -f ~/.hermes/SOUL.md && echo yes); '
                 f'echo OCR=$(test -f ~/.hermes/skills/ocr/ocr.py && echo yes); '
                 f'echo MAILBOX=$(test -d ~/agent_mailbox && echo yes); '
                 f'echo VAULT=$(ls /sparksphear/ | head -1)"')
host_script = "\n".join(lines) + "\n"
with open(r"C:\Users\shaza\Desktop\SparkSphear_App\verify_final.sh","w",newline="\n") as f:
    f.write(host_script)
r = subprocess.run(f'scp -o StrictHostKeyChecking=no "C:\\Users\\shaza\\Desktop\\SparkSphear_App\\verify_final.sh" root@{HOST}:/tmp/verify_final.sh', shell=True, capture_output=True, text=True, timeout=30)
out = subprocess.run(f'ssh -o StrictHostKeyChecking=no root@{HOST} "bash /tmp/verify_final.sh 2>&1"', shell=True, capture_output=True, text=True, timeout=200)
print(out.stdout.strip())
print("ERR:", out.stderr.strip()[:200])