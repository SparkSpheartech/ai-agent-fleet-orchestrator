#!/bin/bash
set -e
cat > /tmp/gfix_120.sh <<'GUESTEOF'
H=$(openssl passwd -6 'REPLACE_WITH_YOUR_VM_PASSWORD')
id onyx >/dev/null 2>&1 || useradd -m -s /bin/bash onyx
usermod -p "$H" onyx
usermod -aG sudo onyx
echo 'onyx ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/onyx
chmod 440 /etc/sudoers.d/onyx
echo FIXED_onyx
GUESTEOF
qm guest exec 120 -- bash -c "$(cat /tmp/gfix_120.sh)"
cat > /tmp/gfix_121.sh <<'GUESTEOF'
H=$(openssl passwd -6 'REPLACE_WITH_YOUR_VM_PASSWORD')
id daisy >/dev/null 2>&1 || useradd -m -s /bin/bash daisy
usermod -p "$H" daisy
usermod -aG sudo daisy
echo 'daisy ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/daisy
chmod 440 /etc/sudoers.d/daisy
echo FIXED_daisy
GUESTEOF
qm guest exec 121 -- bash -c "$(cat /tmp/gfix_121.sh)"
cat > /tmp/gfix_122.sh <<'GUESTEOF'
H=$(openssl passwd -6 'REPLACE_WITH_YOUR_VM_PASSWORD')
id eissa >/dev/null 2>&1 || useradd -m -s /bin/bash eissa
usermod -p "$H" eissa
usermod -aG sudo eissa
echo 'eissa ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/eissa
chmod 440 /etc/sudoers.d/eissa
echo FIXED_eissa
GUESTEOF
qm guest exec 122 -- bash -c "$(cat /tmp/gfix_122.sh)"
cat > /tmp/gfix_123.sh <<'GUESTEOF'
H=$(openssl passwd -6 'REPLACE_WITH_YOUR_VM_PASSWORD')
id shima >/dev/null 2>&1 || useradd -m -s /bin/bash shima
usermod -p "$H" shima
usermod -aG sudo shima
echo 'shima ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/shima
chmod 440 /etc/sudoers.d/shima
echo FIXED_shima
GUESTEOF
qm guest exec 123 -- bash -c "$(cat /tmp/gfix_123.sh)"
cat > /tmp/gfix_124.sh <<'GUESTEOF'
H=$(openssl passwd -6 'REPLACE_WITH_YOUR_VM_PASSWORD')
id travis >/dev/null 2>&1 || useradd -m -s /bin/bash travis
usermod -p "$H" travis
usermod -aG sudo travis
echo 'travis ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/travis
chmod 440 /etc/sudoers.d/travis
echo FIXED_travis
GUESTEOF
qm guest exec 124 -- bash -c "$(cat /tmp/gfix_124.sh)"
echo ALL_DONE
