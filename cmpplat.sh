#!/bin/bash
# Compare Shima vs Daisy telegram platform enable state.
for vm in 123:shima 121:daisy; do
  id=${vm%%:*}; u=${vm##*:}
  echo "===== VM $id ($u) platforms.telegram block ====="
  qm guest exec "$id" -- python3 -c "
import re
p='/home/$u/.hermes/config.yaml'
s=open(p).read()
# find platforms: section
i=s.find('platforms:')
j=s.find('\n'+'gateway:', i)
block=s[i:j]
# locate telegram under platforms
ti=block.find('telegram:')
seg=block[ti:ti+400]
lines=[l for l in seg.splitlines() if 'enabled' in l or 'telegram' in l or 'token' in l.lower()]
print('\n'.join(lines))
" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('out-data','').replace('\\\\n','\n'))" 2>/dev/null
done
echo DONE
