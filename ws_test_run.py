import subprocess

HOST = "192.0.2.100"
# Test via host sshpass ssh (proven pattern) - simple prompt, no special chars
script = r'''
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null onyx@192.0.2.229 "cd /home/onyx && timeout 90 /usr/local/lib/hermes-agent/venv/bin/hermes -z 'Say hello in two words.' 2>&1 | tail -3" > /tmp/ws.log 2>&1
cat /tmp/ws.log
'''
with open(r"C:\Users\shaza\Desktop\SparkSphear_App\ws_test.sh","w",newline="\n") as f:
    f.write(script)
r = subprocess.run(f'scp -o StrictHostKeyChecking=no "C:\\Users\\shaza\\Desktop\\SparkSphear_App\\ws_test.sh" root@{HOST}:/tmp/ws_test.sh', shell=True, capture_output=True, text=True, timeout=30)
out = subprocess.run(f'ssh -o StrictHostKeyChecking=no root@{HOST} "bash /tmp/ws_test.sh"', shell=True, capture_output=True, text=True, timeout=120)
print(out.stdout.strip())
print("ERR:", out.stderr.strip()[:120])