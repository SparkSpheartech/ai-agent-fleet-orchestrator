import subprocess

HOST = "192.0.2.100"
# Grab ShaylasVM service files
script = r'''
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null shayla@192.0.2.228 "echo '=== hermes.service ==='; sudo cat /etc/systemd/system/hermes.service; echo '=== hermes-gateway.service ==='; sudo cat /etc/systemd/system/hermes-gateway.service; echo '=== user gateway ==='; ls ~/.config/systemd/user/ 2>/dev/null" > /tmp/svc_files.log 2>&1
cat /tmp/svc_files.log
'''
with open(r"C:\Users\shaza\Desktop\SparkSphear_App\get_svcs.sh","w",newline="\n") as f:
    f.write(script)
r = subprocess.run(f'scp -o StrictHostKeyChecking=no "C:\\Users\\shaza\\Desktop\\SparkSphear_App\\get_svcs.sh" root@{HOST}:/tmp/get_svcs.sh', shell=True, capture_output=True, text=True, timeout=30)
out = subprocess.run(f'ssh -o StrictHostKeyChecking=no root@{HOST} "bash /tmp/get_svcs.sh"', shell=True, capture_output=True, text=True, timeout=60)
print(out.stdout.strip())
print("ERR:", out.stderr.strip()[:200])