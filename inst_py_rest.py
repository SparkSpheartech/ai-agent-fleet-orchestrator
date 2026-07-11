import subprocess, json

HOST = "192.0.2.100"
def ssh_host(cmd, timeout=200):
    r = subprocess.run(f'ssh -o StrictHostKeyChecking=no root@{HOST} "{cmd}"',
                       shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip()

vms = {120:"onyx",122:"eissa",123:"shima",124:"travis"}
for vmid, user in vms.items():
    fix = ("apt-get install -y software-properties-common >/dev/null 2>&1; "
           "add-apt-repository -y ppa:deadsnakes/ppa >/dev/null 2>&1; "
           "apt-get update >/dev/null 2>&1; "
           "apt-get install -y python3.11 python3.11-venv >/dev/null 2>&1; "
           "echo VER=$(/usr/local/lib/hermes-agent/venv/bin/hermes --version 2>&1 | head -1)")
    out = ssh_host(f"qm guest exec {vmid} -- bash -c '{fix}' 2>&1", timeout=200)
    try:
        d = json.loads(out); res = [l for l in d.get("out-data","").splitlines() if "VER=" in l]
    except: res = [out[:100]]
    print(f"VM{vmid} ({user}): {res}")