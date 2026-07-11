import subprocess

HOST = "192.0.2.100"
script = r'''
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null shayla@192.0.2.228 "echo '=== venv bin ==='; ls /usr/local/lib/hermes-agent/bin/ 2>/dev/null | head; echo '=== hermes in bin? ==='; ls -la /usr/local/lib/hermes-agent/bin/hermes 2>/dev/null; echo '=== systemd user ==='; systemctl --user list-units 2>/dev/null | grep -i hermes; echo '=== gateway service ==='; ls /etc/systemd/system/ | grep -i hermes; ls ~/.config/systemd/user/ 2>/dev/null | grep -i hermes; echo '=== find hermes bin ==='; find /usr/local/lib/hermes-agent -name hermes -type f 2>/dev/null | head; echo '=== pip show ==='; /usr/local/lib/hermes-agent/bin/python -c 'import hermes; print(hermes.__file__)' 2>&1 | head -2" > /tmp/p2.log 2>&1
cat /tmp/p2.log
'''
with open(r"C:\Users\shaza\Desktop\SparkSphear_App\probe2.sh","w",newline="\n") as f:
    f.write(script)
r = subprocess.run(f'scp -o StrictHostKeyChecking=no "C:\\Users\\shaza\\Desktop\\SparkSphear_App\\probe2.sh" root@{HOST}:/tmp/probe2.sh', shell=True, capture_output=True, text=True, timeout=30)
out = subprocess.run(f'ssh -o StrictHostKeyChecking=no root@{HOST} "bash /tmp/probe2.sh"', shell=True, capture_output=True, text=True, timeout=60)
print(out.stdout.strip())
print("ERR:", out.stderr.strip()[:200])