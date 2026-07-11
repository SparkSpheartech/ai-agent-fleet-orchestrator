import subprocess, os, shutil

HOST = "192.0.2.100"
SRC_VAULT = r"G:\My Drive\SPARKSPHEAR VAULT"
STAGE = r"C:\Users\shaza\Desktop\SparkSphear_App\vault_stage"
DST = "/mnt/pve/sparksphear_shared"

folders = ["01_Business_&_Legal", "02_Team_&_HR", "04_Clients"]

# 1. Robocopy each folder to local stage, excluding Drive placeholder types
#    /S copies subdirs, /XF excludes by extension, /R:1 /W:1 fast retry
for f in folders:
    src = os.path.join(SRC_VAULT, f)
    dst = os.path.join(STAGE, f)
    cmd = (f'robocopy "{src}" "{dst}" /S /R:1 /W:1 /NFL /NDL /NJH /NJS '
           f'/XF *.gdoc *.gsheet *.gslides *.gvid *.gform *.gshortcut *.gtable')
    print(f"=== stage {f} ===")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
    print("rc=", r.returncode, "copied lines:", [l for l in r.stdout.splitlines() if 'Copied' in l or 'Bytes' in l][:2])

# 2. Also stage Team_Overview.md
to = os.path.join(STAGE, "Team_Overview.md")
os.makedirs(os.path.dirname(to), exist_ok=True) if False else None
shutil.copy2(r"G:\My Drive\SPARKSPHEAR VAULT\03_Development\Sparkspheartechsolutions_Vault\Vault\3_Agent_Team\Team_Overview.md", to)
print("Team_Overview staged")

# 3. scp the staged tree (real files only) to host
print("\n=== scp staged -> host ===")
r = subprocess.run(f'scp -o StrictHostKeyChecking=no -r "{STAGE}/." root@{HOST}:"{DST}/"',
                   shell=True, capture_output=True, text=True, timeout=400)
print("OUT:", r.stdout.strip()[:200], "ERR:", r.stderr.strip()[:200])
print("DONE")