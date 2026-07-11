import subprocess

HOST = "192.0.2.100"
SRC_VAULT = r"G:\My Drive\SPARKSPHEAR VAULT"
DST = "/mnt/pve/sparksphear_shared"

folders = [
    "01_Business_&_Legal",
    "02_Team_&_HR",
    "04_Clients",
]

def run(cmd, timeout=300):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    print("OUT:", r.stdout.strip()[:300])
    print("ERR:", r.stderr.strip()[:300])
    return r

for f in folders:
    src = f'"{SRC_VAULT}\\{f}"'
    # scp -r source/* into DST/f  (use the folder itself)
    cmd = f'scp -o StrictHostKeyChecking=no -r {src} root@{HOST}:"{DST}/"'
    print(f"\n=== scp {f} ===")
    run(cmd)

# Also copy Team_Overview.md and STRUCTURE-ish docs
team_src = r"G:\My Drive\SPARKSPHEAR VAULT\03_Development\Sparkspheartechsolutions_Vault\Vault\3_Agent_Team\Team_Overview.md"
run(f'scp -o StrictHostKeyChecking=no "{team_src}" root@{HOST}:"{DST}/"')
print("\nDONE")