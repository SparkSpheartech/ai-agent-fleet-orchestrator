#!/bin/bash
# Weekly Hermes fleet maintenance. Runs on Proxmox host (cron: Sat 04:00).
# For each agent VM: verify running, clean zombie hermes procs, update Hermes,
# restart gateway, confirm Telegram reconnect, report.
# Telegram delivery uses the Bot API directly (hermes send is unreliable in v0.18.2).

LOG=/root/hermes_weekly_$(date +%Y%m%d).log
NFS=/mnt/pve/sparksphear_shared 2>/dev/null
exec > >(tee -a "$LOG") 2>&1

echo "============================================================"
echo " Hermes Fleet Weekly Maintenance - $(date)"
echo "============================================================"

# VM list: id:user:ip
VMS="119:shayla:192.0.2.228 121:daisy:192.0.2.230 122:eissa:192.0.2.231 123:shima:192.0.2.232 124:travis:192.0.2.233"

REPORT="🔧 Hermes Fleet Weekly Maintenance — $(date +%Y-%m-%d)
"

for entry in $VMS; do
  id=${entry%%:*}; rest=${entry#*:}; u=${rest%%:*}; ip=${rest##*:}
  echo "------------------------------------------------------------"
  echo ">> VM $id ($u @ $ip)"
  REPORT+="
▸ VM $id ($u): "

  # 1. Is the VM running?
  state=$(qm status "$id" 2>/dev/null | awk '{print $2}')
  if [ "$state" != "running" ]; then
    echo "   [WARN] VM not running (state=$state) — attempting start"
    qm start "$id" 2>&1
    sleep 20
    state=$(qm status "$id" 2>/dev/null | awk '{print $2}')
  fi
  if [ "$state" != "running" ]; then
    echo "   [FAIL] VM $id cannot be started — skipping"
    REPORT+="❌ VM not running, skipped"
    continue
  fi

  # 2. SSH reachability (host key-auth already set up)
  if ! ssh -o StrictHostKeyChecking=no -o ConnectTimeout=15 root@$ip "true" 2>/dev/null; then
    echo "   [FAIL] SSH unreachable — skipping"
    REPORT+="❌ SSH unreachable"
    continue
  fi

  # 3. Clean messed-up / orphan hermes processes (anything not under systemd)
  echo "   [clean] checking for orphan hermes processes"
  ssh -o StrictHostKeyChecking=no root@$ip "
    rm -f /home/$u/.hermes/kanban/.dispatcher.lock 2>/dev/null
    cnt=\$(pgrep -c -u $u -f 'hermes gateway')
    if [ \"\$cnt\" -gt 1 ]; then
      echo '   multiple gateway procs (\$cnt) — killing orphans'
      pkill -9 -u $u -f 'hermes gateway'; sleep 2
    fi
  " 2>&1

  # 4. Update Hermes to latest version (run AS the agent user, not root,
  #    otherwise it corrupts the user-owned venv and deletes the binary)
  echo "   [update] hermes update --yes (as $u)"
  upd=$(ssh -o StrictHostKeyChecking=no root@$ip "su - $u -c 'cd /home/$u && /usr/local/lib/hermes-agent/venv/bin/hermes update --yes 2>&1 | tail -6'" 2>&1)
  if echo "$upd" | grep -qiE 'up to date|already up to date|updated|installed'; then
    up_summary=$(echo "$upd" | grep -iE 'up to date|updated|installed' | head -1 | tr -d '\n' | cut -c1-80)
    REPORT+="update:${up_summary:-done} "
  else
    # Non-fatal: repo dirty / no network / permission — agents stay on current version
    echo "   [note] update skipped ($(echo "$upd" | grep -iE 'failed|denied|dubious|stash' | head -1 | tr -d '\n' | cut -c1-60))"
    REPORT+="update:skipped(repo-not-clean) "
  fi
  echo "   $upd" | head -6

  # 5. Restart the gateway cleanly (kill all, let systemd spawn exactly one)
  echo "   [restart] gateway"
  ssh -o StrictHostKeyChecking=no root@$ip "
    pkill -9 -u $u -f 'hermes gateway' 2>/dev/null; sleep 2
    systemctl start hermes-gateway 2>/dev/null
    sleep 6
  " 2>&1

  # 6. Verify: gateway process alive + telegram connected (retry up to 30s).
  # Note: systemd may report 'activating' even when the process is healthy and
  # connected (quirk with external kills on Type=simple units), so we judge
  # success on the actual process + Telegram connection, not just is-active.
  veri=""
  for attempt in 1 2 3 4 5 6; do
    veri=$(ssh -o StrictHostKeyChecking=no root@$ip "
      active=\$(systemctl is-active hermes-gateway)
      proc=\$(pgrep -c -u $u -f hermes)
      tg=\$(grep -c 'telegram connected' /home/$u/.hermes/logs/gateway.log 2>/dev/null)
      ver=\$(su - $u -c '/usr/local/lib/hermes-agent/venv/bin/hermes --version 2>/dev/null' | head -1)
      echo \"active=\$active proc=\$proc tglines=\$tg ver=\$ver\"
    " 2>&1)
    if echo "$veri" | grep -qE "proc=[1-9]" && echo "$veri" | grep -q "tglines=[1-9]"; then
      break
    fi
    sleep 5
  done
  echo "   [verify] $veri"
  REPORT+="| $veri"

  # mark ok/fail
  if echo "$veri" | grep -qE "proc=[1-9]" && echo "$veri" | grep -q "tglines=[1-9]"; then
    REPORT+=" OK"
  else
    REPORT+=" WARN"
  fi
done

echo "============================================================"
echo " Maintenance complete — $(date)"
echo "============================================================"

# Copy report to NFS if mounted
if mountpoint -q /mnt/pve/sparksphear_shared 2>/dev/null; then
  cp "$LOG" /mnt/pve/sparksphear_shared/hermes_weekly_$(date +%Y%m%d).log 2>/dev/null
fi

# Deliver report to your Telegram via each VM's bot (first one that works wins).
# Write report to a file to avoid quoting/length issues over SSH.
echo ">> Delivering report to Telegram"
# Build a clean single-line report (strip control chars, cap length)
printf '%s' "$REPORT" | tr '\n' ' ' | tr -d '\r' | sed 's/[^[:print:]]//g' | cut -c1-4000 > /root/hermes_report_msg.txt
for entry in $VMS; do
  id=${entry%%:*}; rest=${entry#*:}; u=${rest%%:*}; ip=${rest##*:}
  if ssh -o StrictHostKeyChecking=no root@$ip "true" 2>/dev/null; then
    cat /root/hermes_report_msg.txt | ssh -o StrictHostKeyChecking=no root@$ip "python3 /home/$u/tg_send.py $u 7018094108" 2>&1 && break
  fi
done
echo "DONE"
