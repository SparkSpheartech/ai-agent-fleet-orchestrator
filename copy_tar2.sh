
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null shayla@192.0.2.228:/tmp/hermes_agent.tar.gz /tmp/hermes_agent.tar.gz 2>&1
echo SCP_RC=$?
ls -la /tmp/hermes_agent.tar.gz
