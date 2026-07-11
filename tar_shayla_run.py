import subprocess

HOST = "192.0.2.100"
# Tar ShaylasVM hermes-agent dir -> host /tmp, then we'll push to each VM
script = r'''
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null shayla@192.0.2.228 "tar czf /tmp/hermes_agent.tar.gz -C /usr/local/lib hermes-agent 2>&1; echo TAR_DONE; ls -la /tmp/hermes_agent.tar.gz"
'''
with open(r"C:\Users\shaza\Desktop\SparkSphear_App\tar_shayla.sh","w",newline="\n") as f:
    f.write(script)
r = subprocess.run(f'scp -o StrictHostKeyChecking=no "C:\\Users\\shaza\\Desktop\\SparkSphear_App\\tar_shayla.sh" root@{HOST}:/tmp/tar_shayla.sh', shell=True, capture_output=True, text=True, timeout=30)
out = subprocess.run(f'ssh -o StrictHostKeyChecking=no root@{HOST} "bash /tmp/tar_shayla.sh"', shell=True, capture_output=True, text=True, timeout=120)
print(out.stdout.strip())
print("ERR:", out.stderr.strip()[:200])