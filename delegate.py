#!/usr/bin/env python3
"""
delegate.py - drop a task onto the SparkSphear agent collaboration bus.

Usage:
  delegate.py --to <agent|all|any> --title "..." --prompt "..." [--skills a,b] [--workdir /sparksphear/03_Shared_Workspace/x]
  delegate.py --broadcast --title "..." --prompt "..."

Example (Daisy asks Eissa a research question):
  delegate.py --to eissa --title "TAM for HVAC leads in Fort Wayne" \
    --prompt "Research the total addressable market for residential HVAC in Fort Wayne IN and write a markdown summary to /sparksphear/03_Shared_Workspace/hvac_tam.md" \
    --skills research

The target agent's poller claims the task (atomic), runs it via hermes -z,
and posts the result to /sparksphear/_agent_mailbox/tasks/results/.
"""
import os, sys, json, argparse, datetime, secrets

MAILBOX = "/sparksphear/_agent_mailbox"
# Determine the calling agent's identity robustly:
# prefer the AGENT_NAME env (set by the poller), then $USER/$SUDO_USER,
# then the home-dir basename. Never report "root" unless nothing else is set.
def _agent_name():
    for v in (os.environ.get("AGENT_NAME"), os.environ.get("SUDO_USER"),
              os.environ.get("USER"), os.environ.get("LOGNAME")):
        if v and v != "root":
            return v
    h = os.path.basename(os.path.expanduser("~"))
    return h if h and h != "/" else "unknown"
AGENT = _agent_name()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", default="any")
    ap.add_argument("--title", required=True)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--skills", default="")
    ap.add_argument("--workdir", default="")
    ap.add_argument("--broadcast", action="store_true")
    ap.add_argument("--priority", default="normal")
    a = ap.parse_args()

    pending = os.path.join(MAILBOX, "tasks", "pending")
    broadcast = os.path.join(MAILBOX, "broadcast")
    os.makedirs(pending, exist_ok=True)

    if a.broadcast:
        ts = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
        fn = os.path.join(broadcast, f"{AGENT}_{ts}.md")
        with open(fn, "w") as f:
            f.write(f"# Broadcast from {AGENT}\n\n**{a.title}**\n\n{a.prompt}\n")
        print(f"broadcasted -> {fn}")
        return

    tid = "task_" + secrets.token_hex(6)
    task = {
        "id": tid,
        "from": AGENT,
        "to": a.to,
        "created": datetime.datetime.now().isoformat(timespec="seconds"),
        "title": a.title,
        "prompt": a.prompt,
        "skills": [s.strip() for s in a.skills.split(",") if s.strip()],
        "workdir": a.workdir or "",
        "priority": a.priority,
    }
    path = os.path.join(pending, f"{tid}.json")
    with open(path, "w") as f:
        json.dump(task, f, indent=2)
    print(f"delegated -> {path} (to={a.to})")
    print(f"Result will appear at {MAILBOX}/tasks/results/{tid}.json")

if __name__ == "__main__":
    main()
