import subprocess, json

HOST = "192.0.2.100"
def ssh_host(cmd, timeout=120):
    r = subprocess.run(f'ssh -o StrictHostKeyChecking=no root@{HOST} "{cmd}"',
                       shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip()

vms = {120:"onyx",121:"daisy",122:"eissa",123:"shima",124:"travis"}
for vmid, user in vms.items():
    # Install python3.11 (the venv needs it), then test hermes
    fix = ("apt-get install -y python3.11 python3.11-venv >/dev/null 2>&1; "
           "echo PY=$(/usr/local/share/uv/python/cpython-3.11-linux-x86_64-gnu/bin/python3.11 --version 2>&1); "
           "echo VER=$(/usr/local/lib/hermes-agent/venv/bin/hermes --version 2>&1)")
    out = ssh_host(f"qm guest exec {vmid} -- bash -c '{fix}' 2>&1", timeout=120)
    try:
        d = json.loads(out); res = [l for l in d.get("out-data","").splitlines() if l.startswith(("PY=","VER="))]
    except: res = [out[:100]]
    print(f"VM{vmid} ({user}): {res}")