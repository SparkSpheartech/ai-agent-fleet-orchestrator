import subprocess

HOST = "192.0.2.100"
script = r'''
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null shayla@192.0.2.228 "echo WHICH=$(which hermes); echo REAL=$(readlink -f $(which hermes)); echo ---; ls /usr/local/lib/hermes-agent 2>/dev/null | head; echo ---SERVICE---; cat /etc/systemd/system/hermes-agent.service 2>/dev/null" > /tmp/shayla_probe.log 2>&1
cat /tmp/shayla_probe.log
'''
with open(r"C:\Users\shaza\Desktop\SparkSphear_App\probe_shayla.sh","w",newline="\n") as f:
    f.write(script)
r = subprocess.run(f'scp -o StrictHostKeyChecking=no "C:\\Users\\shaza\\Desktop\\SparkSphear_App\\probe_shayla.sh" root@{HOST}:/tmp/probe_shayla.sh', shell=True, capture_output=True, text=True, timeout=30)
out = subprocess.run(f'ssh -o StrictHostKeyChecking=no root@{HOST} "bash /tmp/probe_shayla.sh"', shell=True, capture_output=True, text=True, timeout=60)
print(out.stdout.strip())
print("ERR:", out.stderr.strip()[:200])