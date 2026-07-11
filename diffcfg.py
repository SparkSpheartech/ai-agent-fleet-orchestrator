#!/bin/bash
# Diff Shima vs Daisy configs to find why Shima gateway sees 'no platforms'.
python3 - <<'PY'
import subprocess, json
def cfg(vm,u):
    out=subprocess.run(['qm','guest','exec',vm,'--','python3','-c',
        "import yaml,json;d=yaml.safe_load(open('/home/%s/.hermes/config.yaml'));print(json.dumps(d.get('platforms',{})))"%u],
        capture_output=True,text=True)
    try:
        d=json.loads(out.stdout)
        return d
    except Exception as e:
        return {"_raw":out.stdout[:500],"_err":str(e)}
for vm,u in [("123","shima"),("121","daisy")]:
    print("==== %s (%s) platforms ===="%(vm,u))
    print(json.dumps(cfg(vm,u),indent=1)[:1500])
PY
echo DONE
