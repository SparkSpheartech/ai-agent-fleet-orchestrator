#!/bin/bash
for vm_u in "123:shima" "121:daisy"; do
  vm=${vm_u%%:*}; u=${vm_u##*:}
  echo "==== VM $vm ($u) .env (keys only, masked) ===="
  qm guest exec "$vm" -- bash -c "grep -iE '^[A-Z_]*=' /home/$u/.hermes/.env | sed -E 's/=(.{0,10}).*/=\1.../' | sort" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('out-data','').replace('\\\\n','\n'))" 2>/dev/null
  echo "---- gateway-enabled key in config? ----"
  qm guest exec "$vm" -- python3 -c "
import yaml
d=yaml.safe_load(open('/home/$u/.hermes/config.yaml'))
print('platforms keys:', list(d.get('platforms',{}).keys()))
tg=d.get('telegram',{})
print('top telegram:', {k:tg[k] for k in list(tg)[:6] if k in tg})
" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('out-data','').replace('\\\\n','\n'))" 2>/dev/null
done
echo DONE
