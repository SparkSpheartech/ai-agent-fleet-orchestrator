import subprocess

HOST = "192.0.2.100"
# Test: create venv + install hermes-agent on VM120 (quick check it works)
script = r'''
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null onyx@192.0.2.229 "python3 -m venv /usr/local/lib/hermes-agent/venv 2>&1 | tail -1; /usr/local/lib/hermes-agent/venv/bin/pip install --quiet hermes-agent 2>&1 | tail -3; echo INSTALL_RC=$?" > /tmp/inst120.log 2>&1
cat /tmp/inst120.log
'''
with open(r"C:\Users\shaza\Desktop\SparkSphear_App\inst_test.sh","w",newline="\n") as f:
    f.write(script)
r = subprocess.run(f'scp -o StrictHostKeyChecking=no "C:\\Users\\shaza\\Desktop\\SparkSphear_App\\inst_test.sh" root@{HOST}:/tmp/inst_test.sh', shell=True, capture_output=True, text=True, timeout=30)
out = subprocess.run(f'ssh -o StrictHostKeyChecking=no root@{HOST} "nohup bash /tmp/inst_test.sh >/tmp/inst120.log 2>&1 & echo STARTED"', shell=True, capture_output=True, text=True, timeout=30)
print("launch:", out.stdout.strip(), out.stderr.strip()[:80])