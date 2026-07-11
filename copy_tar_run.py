import subprocess

HOST = "192.0.2.100"
# Copy tar from ShaylasVM to host /tmp (host-to-host, fast)
script = r'''
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null shayla@192.0.2.228:/tmp/hermes_agent.tar.gz /tmp/hermes_agent.tar.gz 2>&1
echo SCP_RC=$?
ls -la /tmp/hermes_agent.tar.gz
'''
with open(r"C:\Users\shaza\Desktop\SparkSphear_App\copy_tar.sh","w",newline="\n") as f:
    f.write(script)
r = subprocess.run(f'scp -o StrictHostKeyChecking=no "C:\\Users\\shaza\\Desktop\\SparkSphear_App\\copy_tar.sh" root@{HOST}:/tmp/copy_tar.sh', shell=True, capture_output=True, text=True, timeout=30)
out = subprocess.run(f'ssh -o StrictHostKeyChecking=no root@{HOST} "nohup bash /tmp/copy_tar.sh >/tmp/copytar.log 2>&1 & echo STARTED"', shell=True, capture_output=True, text=True, timeout=30)
print("launch:", out.stdout.strip())