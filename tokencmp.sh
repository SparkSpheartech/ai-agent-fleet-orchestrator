#!/bin/bash
declare -A U=( [119]=shayla [120]=onyx [121]=daisy [122]=eissa [123]=shima [124]=travis )
for id in 119 120 121 122 123 124; do
  u=${U[$id]}
  qm guest exec "$id" -- bash -c "
    H=/home/$u
    cd \$H/.hermes
    T=\$(grep -iE 'TELEGRAM_BOT_TOKEN' .env 2>/dev/null | head -1 | cut -d= -f2-)
    [ -z \"\$T\" ] && T=\$(grep -iE 'bot_token' config.yaml 2>/dev/null | head -1 | awk '{print \$2}')
    if [ -n \"\$T\" ]; then PREFIX=\$(echo \$T | cut -c1-8); SUFFIX=\$(echo \$T | rev | cut -c1-6 | rev); echo ID$id $u token:\${PREFIX}..._\${SUFFIX}; else echo ID$id $u NO_TOKEN; fi
  " 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('out-data','').replace('\\\\n','\n'))" 2>/dev/null
done
echo DONE
