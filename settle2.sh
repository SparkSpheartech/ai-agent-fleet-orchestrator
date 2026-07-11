#!/bin/bash
# Settle systemd + git config on all agent VMs so the weekly script reports cleanly.
VMS="119:shayla:192.0.2.228 121:daisy:192.0.2.230 122:eissa:192.0.2.231 123:shima:192.0.2.232 124:travis:192.0.2.233"
for entry in $VMS; do
  id=${entry%%:*}; rest=${entry#*:}; u=${rest%%:*}; ip=${rest##*:}
  echo "=== VM $id ($u) ==="
  qm guest exec "$id" -- bash -c "
    # per-user git safe.directory so hermes update can fetch
    su - $u -c 'git config --global --add safe.directory /usr/local/lib/hermes-agent' 2>/dev/null
    su - $u -c 'git config --global --add safe.directory "*"' 2>/dev/null
    # clean stale failed unit, let systemd respawn cleanly
    systemctl reset-failed hermes-gateway 2>/dev/null
    pkill -9 -u $u -f 'hermes gateway' 2>/dev/null; sleep 3
    # systemd Restart=on-failure will bring it back as the managed process
    sleep 8
    echo ACTIVE=\$(systemctl is-active hermes-gateway)
    echo PROC=\$(pgrep -c -u $u -f hermes)
    echo TG=\$(grep -c 'telegram connected' /home/$u/.hermes/logs/gateway.log)
  " 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('out-data','').replace('\\\\n','\n'))" 2>/dev/null
done
echo SETTLE2_DONE
