import subprocess, json

HOST = "192.0.2.100"
def ssh_host(cmd, timeout=90):
    r = subprocess.run(f'ssh -o StrictHostKeyChecking=no root@{HOST} "{cmd}"',
                       shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip()

vms = {120:"onyx",121:"daisy",122:"eissa",123:"shima",124:"travis"}

# Start VM120 if stopped
print("start 120:", ssh_host("qm start 120 2>&1; sleep 3; qm status 120", timeout=60))

for vmid, user in vms.items():
    # Create the uv-managed python path the venv expects, symlinked to system python3.11
    fix = ("mkdir -p /usr/local/share/uv/python/cpython-3.11-linux-x86_64-gnu/bin; "
           "ln -sfn /usr/bin/python3.11 /usr/local/share/uv/python/cpython-3.11-linux-x86_64-gnu/bin/python3.11; "
           "ln -sfn /usr/bin/python3.11 /usr/local/share/uv/python/cpython-3.11-linux-x86_64-gnu/bin/python3; "
           "echo VER=$(/usr/local/lib/hermes-agent/venv/bin/hermes --version 2>&1)")
    out = ssh_host(f"qm guest exec {vmid} -- bash -c '{fix}' 2>&1", timeout=60)
    try:
        d = json.loads(out); res = [l for l in d.get("out-data","").splitlines() if "VER=" in l]
    except: res = [out[:100]]
    print(f"VM{vmid} ({user}): {res}")