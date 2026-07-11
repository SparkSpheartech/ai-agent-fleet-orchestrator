import subprocess

HOST = "192.0.2.100"
# Run foreground (host-to-host scp of 2.2GB, should be quick on local network)
script = r'''
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null shayla@192.0.2.228:/tmp/hermes_agent.tar.gz /tmp/hermes_agent.tar.gz 2>&1
echo SCP_RC=$?
ls -la /tmp/hermes_agent.tar.gz
'''
with open(r"C:\Users\shaza\Desktop\SparkSphear_App\copy_tar2.sh","w",newline="\n") as f:
    f.write(script)
r = subprocess.run(f'scp -o StrictHostKeyChecking=no "C:\\Users\\shaza\\Desktop\\SparkSphear_App\\copy_tar2.sh" root@{HOST}:/tmp/copy_tar2.sh', shell=True, capture_output=True, text=True, timeout=30)
out = subprocess.run(f'ssh -o StrictHostKeyChecking=no root@{HOST} "bash /tmp/copy_tar2.sh"', shell=True, capture_output=True, text=True, timeout=200)
print(out.stdout.strip())
print("ERR:", out.stderr.strip()[:150])