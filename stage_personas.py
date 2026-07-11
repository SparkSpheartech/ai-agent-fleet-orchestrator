import subprocess

HOST = "192.0.2.100"
# Push creds + persona files to each VM's ~/.hermes
# creds already on host at /tmp/creds/{config.yaml,auth.json,.env}
# personas on host: need to scp them up first
PERSONAS = ["onyx","daisy","eissa","shima","travis"]
vms = {"onyx":("120","192.0.2.229"),"daisy":("121","192.0.2.230"),
       "eissa":("122","192.0.2.231"),"shima":("123","192.0.2.232"),"travis":("124","192.0.2.233")}

# 1. scp persona files to host
for p in PERSONAS:
    for f in [f"{p}_SOUL.md", f"{p}_USER.md"]:
        src = f"C:\\Users\\shaza\\Desktop\\SparkSphear_App\\personas\\{f}"
        r = subprocess.run(f'scp -o StrictHostKeyChecking=no "{src}" root@{HOST}:/tmp/personas/ 2>/dev/null', shell=True, capture_output=True, text=True, timeout=30)
# ensure host dir
subprocess.run(f'ssh -o StrictHostKeyChecking=no root@{HOST} "mkdir -p /tmp/personas"', shell=True, capture_output=True, text=True, timeout=30)
for p in PERSONAS:
    for f in [f"{p}_SOUL.md", f"{p}_USER.md"]:
        src = f"C:\\Users\\shaza\\Desktop\\SparkSphear_App\\personas\\{f}"
        subprocess.run(f'scp -o StrictHostKeyChecking=no "{src}" root@{HOST}:/tmp/personas/ 2>&1', shell=True, capture_output=True, text=True, timeout=30)
print("personas on host:", subprocess.run(f'ssh -o StrictHostKeyChecking=no root@{HOST} "ls /tmp/personas/"', shell=True, capture_output=True, text=True, timeout=30).stdout.strip())