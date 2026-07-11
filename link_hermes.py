import subprocess, json

HOST = "192.0.2.100"
def ssh_host(cmd, timeout=90):
    r = subprocess.run(f'ssh -o StrictHostKeyChecking=no root@{HOST} "{cmd}"',
                       shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip()

vms = {120:"onyx",121:"daisy",122:"eissa",123:"shima",124:"travis"}
for vmid, user in vms.items():
    # Remove any partial local copy, symlink to NFS install
    fix = ("rm -rf /usr/local/lib/hermes-agent; "
           "ln -sfn /sparksphear/hermes-agent /usr/local/lib/hermes-agent; "
           "ln -sfn /usr/local/lib/hermes-agent/venv/bin/hermes /usr/local/bin/hermes; "
           "chmod +x /usr/local/lib/hermes-agent/venv/bin/hermes 2>/dev/null; "
           "echo VER=$(/usr/local/lib/hermes-agent/venv/bin/hermes --version 2>&1)")
    out = ssh_host(f"qm guest exec {vmid} -- bash -c '{fix}' 2>&1", timeout=60)
    try:
        d = json.loads(out); res = [l for l in d.get("out-data","").splitlines() if "VER=" in l]
    except: res = [out[:100]]
    print(f"VM{vmid} ({user}): {res}")