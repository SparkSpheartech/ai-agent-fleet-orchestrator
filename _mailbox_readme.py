import base64, subprocess

mailbox_readme = r'''# Agent Mailbox & Collaboration Bus

Shared coordination space for the SparkSphear agent fleet
(ShaylasVM, Daisy, Eissa, Shima, Travis). All paths live on the NFS
share mounted at /sparksphear on every agent VM.

## Task delegation protocol
A task is a JSON file. Any agent can drop one into tasks/pending/ to ask
another agent (or all agents) to do work.

Task JSON schema:
{
  "id": "task_<random>",
  "from": "daisy",
  "to": "eissa",                 // target agent, or "all", or "any"
  "created": "2026-07-09T22:00:00",
  "title": "short summary",
  "prompt": "full instructions for the target agent",
  "skills": ["skill-a","skill-b"],   // optional skills to load
  "workdir": "/sparksphear/03_Shared_Workspace/...", // where to write outputs
  "priority": "normal",          // normal | high
  "reply_to": "tasks/results"    // where to drop the result
}

## Lifecycle (handled by /usr/local/bin/agent_poll.py on each VM)
  pending/  ->(atomic claim)-> claimed/<agent>_<id>.json  ->(run)-> running/
           -> on success: results/<id>.json + archive/  ;  on fail: tasks/failed/

Claiming is atomic: rename the file to claimed/<agent>_<id>.json with mv
(NFS-safe), so only one agent ever picks up a given task.

## Direct messages
- inbox/<to>_<from>_<ts>.md  - private note to one agent
- outbox/<from>_<to>_<ts>.md - copy kept by sender
- broadcast/<from>_<ts>.md   - announces to all agents

## Shared workspace
Business files live in /sparksphear (01_Business_&_Legal, 02_Team_&_HR,
04_Clients, 05_Agents). Use 03_Shared_Workspace for collaborative drafts
and working files all agents can read and add to.

## Agent directory
See 05_Agents/README.md for each agent role and how to reach them.
'''

agent_dir_readme = r'''# SparkSphear Agent Directory

All agents run inside their own Proxmox VM, share /sparksphear (NFS), and
collaborate via /sparksphear/_agent_mailbox.

| Agent     | VM   | IP             | Role                    | Telegram bot    |
|-----------|------|----------------|-------------------------|-----------------|
| ShaylasVM | 119  | 192.0.2.228  | Founder CEO orchestrator| main host       |
| Daisy     | 121  | 192.0.2.230  | Operations execution    | SparkDaisy_bot  |
| Eissa     | 122  | 192.0.2.231  | Research analysis       | SparkEissa_bot  |
| Shima     | 123  | 192.0.2.232  | Business architect      | SparkShima_bot  |
| Travis    | 124  | 192.0.2.233  | Engineering build       | SparkTravis_bot |

## How agents delegate
Drop a task JSON into /sparksphear/_agent_mailbox/tasks/pending/
(the target agent poller claims it, runs it via hermes -z, drops the
result into tasks/results/). Or send a direct note to inbox/<agent>_*.
See _agent_mailbox/README.md for the full schema.
'''

mb = base64.b64encode(mailbox_readme.encode()).decode()
ad = base64.b64encode(agent_dir_readme.encode()).decode()

script = f'''
set -e
BASE=/mnt/pve/sparksphear_shared/_agent_mailbox
mkdir -p "$BASE/inbox" "$BASE/outbox" "$BASE/tasks/pending" "$BASE/tasks/claimed" "$BASE/tasks/running" "$BASE/tasks/done" "$BASE/tasks/failed" "$BASE/results" "$BASE/archive" "$BASE/broadcast"
chmod -R 2777 "$BASE"
echo '{mb}' | base64 -d > "$BASE/README.md"
echo '{ad}' | base64 -d > /mnt/pve/sparksphear_shared/05_Agents/README.md
chmod -R a+rwX "$BASE" /mnt/pve/sparksphear_shared/05_Agents
find "$BASE" -type d | sort
echo DONE
'''

r = subprocess.run(
    ['ssh','-o','StrictHostKeyChecking=no','root@192.0.2.100','bash','-s'],
    input=script, capture_output=True, text=True, timeout=90)
print("RC", r.returncode)
print(r.stdout[-1500:])
print(r.stderr[-800:])
