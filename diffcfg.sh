#!/bin/bash
# Run on proxmox host. Diffs Shima vs Daisy 'platforms' from parsed yaml.
for vm_u in "123:shima" "121:daisy"; do
  vm=${vm_u%%:*}; u=${vm_u##*:}
  echo "==== VM $vm ($u) platforms (parsed) ===="
  qm guest exec "$vm" -- python3 -c "
import yaml,json
d=yaml.safe_load(open('/home/$u/.hermes/config.yaml'))
print(json.dumps(d.get('platforms',{}),indent=1))
" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('out-data','').replace('\\\\n','\n'))" 2>/dev/null
done
echo DONE
