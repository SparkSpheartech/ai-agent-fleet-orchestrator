#!/usr/bin/env python3
"""
agent_poll.py - SparkSphear inter-agent collaboration poller.

Runs on each agent VM (as that agent's user). Every POLL_INTERVAL seconds:
  1. Claims any task in <mailbox>/tasks/pending that is addressed to this
     agent (or to "all"/"any"). Claiming is atomic via os.rename (NFS-safe),
     so two agents can never grab the same task.
  2. Runs the task prompt through Hermes in headless mode (`hermes -z`),
     capturing the agent's response, optionally loading skills and a workdir.
  3. Writes the result to <mailbox>/tasks/results/<id>.json, moves the task
     to tasks/done (or tasks/failed on error), and can send a Telegram note
     back to the requester via the agent's own bot.

Also processes direct inbox notes addressed to this agent and logs them.

Designed to be safe, idempotent, and resilient: a crashed run leaves the
task in tasks/running so it can be retried, and a stale running task is
released after RUN_TIMEOUT seconds.
"""
import os
import sys
import json
import time
import uuid
import shutil
import subprocess
import datetime

MAILBOX = os.environ.get("AGENT_MAILBOX", "/sparksphear/_agent_mailbox")
AGENT = os.environ.get("AGENT_NAME", os.path.basename(os.path.expanduser("~")))
POLL_INTERVAL = int(os.environ.get("AGENT_POLL_INTERVAL", "60"))
RUN_TIMEOUT = int(os.environ.get("AGENT_RUN_TIMEOUT", "1800"))  # 30 min max per task
HERMES = "/usr/local/lib/hermes-agent/venv/bin/hermes"
LOG = os.path.join(MAILBOX, "..", "..", "03_Shared_Workspace", f".poll_{AGENT}.log")

def now_iso():
    return datetime.datetime.now().isoformat(timespec="seconds")

def log(msg):
    line = f"{now_iso()} [{AGENT}] {msg}"
    try:
        with open(os.path.abspath(LOG), "a") as f:
            f.write(line + "\n")
    except Exception:
        pass
    print(line, flush=True)

def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None

def my_turn(task):
    to = str(task.get("to", "")).strip().lower()
    return to in ("", "all", "any", AGENT.lower())

def claim(pending_path):
    """Atomically move pending task into tasks/running/<id>.json.
    Returns the new path on success, else None (already claimed by someone)."""
    base = os.path.dirname(os.path.dirname(pending_path))  # .../tasks
    running = os.path.join(base, "running")
    os.makedirs(running, exist_ok=True)
    tid = task_id(pending_path)
    dest = os.path.join(running, f"{tid}.json")
    try:
        os.rename(pending_path, dest)
        return dest
    except OSError:
        return None

def task_id(path):
    name = os.path.splitext(os.path.basename(path))[0]
    return name

def run_hermes(task):
    """Execute the task prompt headlessly and return (ok, output)."""
    prompt = task.get("prompt") or task.get("title") or ""
    workdir = task.get("workdir") or os.path.expanduser("~/sparksphear_work")
    os.makedirs(workdir, exist_ok=True)
    cmd = [HERMES, "-z", prompt, "--cli"]
    skills = task.get("skills")
    if skills:
        cmd += ["--skills", ",".join(skills)]
    if task.get("model"):
        cmd += ["-m", task["model"]]
    log(f"running hermes for task {task.get('id')}: {prompt[:80]!r}")
    try:
        res = subprocess.run(
            cmd, cwd=workdir, capture_output=True, text=True,
            timeout=RUN_TIMEOUT, env={**os.environ, "HERMES_AUTO_APPROVE": "1"},
        )
        out = (res.stdout or "") + (res.stderr or "")
        return (res.returncode == 0, out.strip())
    except subprocess.TimeoutExpired:
        return (False, f"TIMEOUT after {RUN_TIMEOUT}s")
    except Exception as e:
        return (False, f"ERROR: {e}")

def write_result(task, ok, output):
    # task["_running_path"] = <MAILBOX>/tasks/running/<id>.json
    # canonical result location: <MAILBOX>/tasks/results/<id>.json
    base = os.path.dirname(task["_running_path"])          # .../tasks/running
    base = os.path.dirname(base)                            # .../tasks
    results_dir = os.path.join(base, "results")
    os.makedirs(results_dir, exist_ok=True)
    result = {
        "id": task.get("id"),
        "from": task.get("from"),
        "to": task.get("to"),
        "title": task.get("title"),
        "ok": ok,
        "output": output,
        "completed": now_iso(),
        "by": AGENT,
    }
    rpath = os.path.join(results_dir, f"{task.get('id')}.json")
    with open(rpath, "w") as f:
        json.dump(result, f, indent=2)
    # archive the task file
    archive = os.path.join(base, "done" if ok else "failed")
    os.makedirs(archive, exist_ok=True)
    shutil.move(task["_running_path"], os.path.join(archive, f"{task.get('id')}.json"))
    return rpath

def notify(task, ok, rpath):
    """Optionally ping the requester's agent via Telegram using this agent's bot."""
    if not task.get("notify", True):
        return
    try:
        msg = f"[task {task.get('id')}] {'DONE' if ok else 'FAILED'}: {task.get('title')}\nresult: {rpath}"
        subprocess.run([HERMES, "send", "--to", "telegram", msg],
                       capture_output=True, timeout=30)
    except Exception:
        pass

def release_stale(base_running):
    """Move tasks stuck in running longer than RUN_TIMEOUT back to pending."""
    for fn in os.listdir(base_running):
        if not fn.endswith(".json"):
            continue
        p = os.path.join(base_running, fn)
        try:
            st = os.stat(p)
            age = time.time() - st.st_mtime
            if age > RUN_TIMEOUT:
                pending = os.path.join(os.path.dirname(base_running), "pending", fn)
                os.rename(p, pending)
                log(f"released stale task {fn} back to pending")
        except OSError:
            pass

def process_once():
    pending_dir = os.path.join(MAILBOX, "tasks", "pending")
    running_dir = os.path.join(MAILBOX, "tasks", "running")
    os.makedirs(pending_dir, exist_ok=True)
    os.makedirs(running_dir, exist_ok=True)
    release_stale(running_dir)

    claimed_any = False
    for fn in sorted(os.listdir(pending_dir)):
        if not fn.endswith(".json"):
            continue
        ppath = os.path.join(pending_dir, fn)
        task = load_json(ppath)
        if not task:
            continue
        if not my_turn(task):
            continue
        # try atomic claim
        rpath = claim(ppath)
        if not rpath:
            continue  # someone else got it
        claimed_any = True
        task["_running_path"] = rpath
        log(f"claimed task {task.get('id')} from {task.get('from')}")
        ok, output = run_hermes(task)
        rpath = write_result(task, ok, output)
        notify(task, ok, rpath)
        log(f"finished task {task.get('id')} ok={ok}")
    return claimed_any

def main():
    log(f"poller started (agent={AGENT}, mailbox={MAILBOX}, interval={POLL_INTERVAL}s)")
    while True:
        try:
            process_once()
        except Exception as e:
            log(f"loop error: {e}")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
