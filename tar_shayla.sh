
sshpass -p "REPLACE_WITH_YOUR_VM_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null shayla@192.0.2.228 "tar czf /tmp/hermes_agent.tar.gz -C /usr/local/lib hermes-agent 2>&1; echo TAR_DONE; ls -la /tmp/hermes_agent.tar.gz"
