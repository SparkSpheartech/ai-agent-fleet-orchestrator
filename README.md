# NebulaForge — SparkSphear AI Agent Fleet & Business Automation Suite

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows-lightgrey.svg)

> **NebulaForge** is the runtime toolkit that powers the SparkSphear AI agent
> fleet: a multi-VM, NFS-backed, message-passing "collaboration bus" that lets
> autonomous AI agents (Hermes) delegate tasks to one another, plus the
> dispatch console, trading backtester, OCR skill factory, and parts-pricing
> engine that run the SparkSphear Tech Solutions business.

This repository is the **sanitized, public build** of the original
`Desktop/SparkSphear_App` workspace. All credentials, bot tokens, client PII,
and personal notes have been removed; internal RFC1918 addresses have been
replaced with RFC5737 `192.0.2.0/24` TEST-NET placeholders so the code reads
cleanly without leaking the private topology.

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [The Agent Collaboration Bus](#the-agent-collaboration-bus)
3. [Component Reference](#component-reference)
4. [Technology Stack](#technology-stack)
5. [Repository Layout](#repository-layout)
6. [Installation](#installation)
7. [Usage](#usage)
8. [Security Model](#security-model)
9. [Roadmap](#roadmap)
10. [License](#license)

---

## System Architecture

```
                         ┌─────────────────────────────────────────┐
                         │   Proxmox VE Host (hypervisor)          │
                         │   ├─ NFS export: /sparksphear           │
                         │   │      (shared by every agent VM)     │
                         │   └─ CT/VM: 120 Onyx · 121 Daisy ·      │
                         │           122 Eissa · 123 Shima ·       │
                         │           124 Travis                    │
                         └───────────────────┬─────────────────────┘
                                             │ NFS mount @ /sparksphear
         ┌───────────────────────────────────┼───────────────────────────────────┐
         │  Each agent VM runs (systemd units):                                    │
         │                                                                         │
         │   svc_hermes.service ──> hermes serve   (Hermes Agent API, headless)    │
         │   agent_poll.service ──> agent_poll.py  (claims + executes tasks)       │
         │   comfyui.service   ──> ComfyUI         (image-gen worker, optional)    │
         │                                                                         │
         │   /sparksphear/_agent_mailbox/                                           │
         │      ├─ tasks/pending   (drop zone)                                      │
         │      ├─ tasks/running   (claimed, in-flight)                             │
         │      ├─ tasks/done      (archived)                                       │
         │      ├─ tasks/failed    (dead-letter)                                    │
         │      ├─ results/        (JSON outputs)                                   │
         │      ├─ inbox/  outbox/  broadcast/  (human/direct msgs)                 │
         └─────────────────────────────────────────────────────────────────────────┘
                                             │
                         ┌───────────────────┴────────────────────┐
                         │  Operator workstation (Windows / Linux) │
                         │   ├─ SparkSphear_Main.py  (Tk dispatch) │
                         │   ├─ delegate.py          (push tasks)  │
                         │   ├─ build_agents*.py     (fleet bring-up)│
                         │   ├─ etf_backtest_strategy.py           │
                         │   └─ smart_pricing_engine.py            │
                         └─────────────────────────────────────────┘
```

### Design principles

* **NFS as the only shared state.** Agents are otherwise stateless. The NFS
  share (`/sparksphear`) is the single source of truth for tasks, results, and
  shared business files. No centralized broker (RabbitMQ/Kafka) is required —
  the filesystem *is* the message queue.
* **Atomic claim via `rename`.** Task ownership is acquired by `os.rename`
  onto `claimed/<agent>_<id>.json`. `rename` is atomic on NFS, so two agents
  can never grab the same task even under concurrency.
* **Idempotent + crash-safe.** A crashed run leaves the task in `tasks/running`
  with a `claimed_by`/`claimed_at` stamp; a stale running task is re-released
  after `RUN_TIMEOUT` seconds and retried.
* **Headless agent execution.** The poller shells out to the Hermes Agent CLI
  in zero-interaction mode (`hermes -z`), optionally injecting `--skills` and
  a `--workdir`, capturing stdout as the result payload.

---

## The Agent Collaboration Bus

The bus is a directory protocol, not a daemon. Any agent (or the operator) can
write a task file to `_agent_mailbox/tasks/pending/` and the targeted agent's
poller will pick it up.

### Task JSON schema

```json
{
  "id": "task_1a2b3c",            // secrets.token_hex(6)
  "from": "daisy",                // originating agent
  "to": "eissa",                  // target: agent name | "all" | "any"
  "created": "2026-07-09T22:00:00",
  "title": "short summary",
  "prompt": "full instructions for the target agent",
  "skills": ["research", "finance"],
  "workdir": "/sparksphear/03_Shared_Workspace/x",
  "priority": "normal",           // normal | high
  "reply_to": "tasks/results"
}
```

### Lifecycle state machine

```
            ┌────────────┐  atomic rename   ┌────────────┐  run (hermes -z)  ┌───────────┐
pending ───▶│ claimed/   │ ───────────────▶ │ running/   │ ───────────────▶ │ done/ +   │
            │<agent>_id  │                  │            │                  │ results/  │
            └────────────┘                  └────────────┘                  └───────────┘
                   ▲                              │  exception / timeout
                   │                              ▼
                   └─────────────── released ──▶  tasks/failed/   (dead-letter, alert)
```

### Direct messaging

| Channel      | File pattern                       | Purpose                       |
|--------------|------------------------------------|-------------------------------|
| `inbox/`     | `<to>_<from>_<ts>.md`              | private note to one agent     |
| `outbox/`    | `<from>_<to>_<ts>.md`              | sender's copy                 |
| `broadcast/` | `<from>_<ts>.md`                   | announce to all agents        |

---

## Component Reference

### Dispatch Console
* **`SparkSphear_Main.py`** — Tkinter GUI (2 tabs: *Main App* + live *Activity
  Log*). Generates client quotes/invoices as PDF (FPDF2), geocodes trip
  distance from the base address, and drives the workflow. Logging is
  file + UI via `logging` with a rotating handler.
* **`SparkSphear_Simple_Working.py`, `SparkSphear_v3_MultiDevice.py`,
  `SparkSphear_v4_IssueList.py`** — progressive iterations of the console.
* **`SparkSphear_Archive/`** — historical app versions (pricing-only,
  smart-pricing-integrated, fully-integrated) preserved for reference.

### Fleet Orchestration
* **`build_agents.py` / `build_agents2.py` / `build_agents3.py`** — bring up
  agent VMs on Proxmox via `qm`/`ssh`, push a cloud-init snippet (password
  auth + qemu-guest-agent + NFS mount), and install the Hermes agent.
* **`deploy_agents.sh` / `deploy_agents2.sh`** — per-VM deployment wrappers.
* **`chk_vms*.sh` / `chk_vms*_run.py`** — health checks (NFS mount, user,
  hostname) across the fleet using its VM→IP map.
* **`fixprereq.sh`, `fixfleet.sh`, `fix_and_test.py`, `finalverify.sh`** —
  prerequisite repair and end-to-end fleet verification.

### Collaboration Bus
* **`agent_poll.py`** — the poller daemon (see [architecture](#system-architecture)).
* **`agent_poll.service`** — systemd unit (`Type=simple`, restarts on failure,
  `After=nfs-client.target`).
* **`delegate.py`** — CLI to drop a task or broadcast onto the bus.
* **`_mailbox_readme.py`** — embeds the canonical mailbox protocol doc.
* **`svc_hermes.service`** — systemd unit launching the Hermes Agent server.
* **`svc_hermes_gateway.service`** — gateway/bridge unit.
* **`comfyui.service`, `comfyui-mcp-shima.service`** — image-generation worker
  + Model Context Protocol bridge for the Shima agent.

### Trading / Quant
* **`etf_backtest_strategy.py`** — backtests long-only strategies on
  Shariah-compliant ETFs (e.g. HLAL, SPUS) using `yfinance` historicals;
  computes RSI, EMA(20/50/200), MACD, and emits concrete next-day sell orders.
* **`etf_sell_signals.py`, `etf_sell_orders_fixed.py`** — signal + order
  generators. **`etf_analysis.json` / `sell_orders_ready.json`** — sample
  outputs. **`cost_matrix.txt`** — fee/slippage model constants.

### Pricing / Scraping
* **`smart_pricing_engine.py`** — SQLite device DB + live eBay/Google Shopping
  parts-cost scraper (BeautifulSoup); suggests 4 replacement options and
  optimal margin. Classes: `DeviceDatabase`, `PricingEngine`.
* **`ocr_tool.py`** — Tesseract/EasyOCR wrapper to extract text from images.
* **`build_ocr_skill.py`** — packages the OCR logic into a reusable Hermes
  skill (`ocr_skill_pkg/ocr`). **`publora_skill.md`** — LoRA/SD skill doc.

### Misc / Utilities
* **`copy_vault.py`, `stage_personas.py`, `stage_and_copy.py`** — Obsidian
  vault + persona staging onto the share.
* **`diffcfg.py`, `cmpenv.sh`, `cmpplat.sh`** — config/env/platform diffing.
* **`hermes_weekly.sh`, `verify_*.sh`, `restart_all.sh`** — ops/CRON helpers.
* **`*.bat` (`Launch_App.bat`, `LAUNCH_SparkSphear.bat`)** — Windows launchers.
* **`logo.jpg` / `logo.png`** — SparkSphear brandmark.

---

## Technology Stack

| Layer        | Tech                                                         |
|--------------|--------------------------------------------------------------|
| UI           | Python `tkinter`, `ttk`                                      |
| PDF          | `fpdf2`, `reportlab`                                         |
| Scraping     | `requests`, `beautifulsoup4`                                |
| OCR          | `pytesseract`, `easyocr`, `Pillow`                          |
| Quant        | `yfinance`, `pandas`, `numpy`                               |
| Data         | `sqlite3` (local), NFS-mounted shared filesystem            |
| Agent runtime| Hermes Agent CLI (`hermes serve`, `hermes -z`)              |
| Infra        | Proxmox VE, QEMU/KVM, cloud-init, systemd, NFSv4            |
| Ops          | `bash`, `sshpass`, `openssl passwd -6` (yescrypt)          |
| Imaging (opt)| ComfyUI + MCP bridge                                        |

---

## Repository Layout

```
NebulaForge/
├── SparkSphear_Main.py          # Tkinter dispatch console (2 tabs)
├── SparkSphear_Simple_Working.py
├── SparkSphear_v3_MultiDevice.py
├── SparkSphear_v4_IssueList.py
├── SparkSphear_Archive/         # historical app versions
├── agent_poll.py                # collaboration-bus poller
├── agent_poll.service           # systemd unit
├── delegate.py                  # task broadcaster CLI
├── _mailbox_readme.py           # bus protocol doc
├── build_agents*.py             # VM bring-up
├── deploy_agents*.sh
├── chk_vms*.sh / *_run.py       # fleet health checks
├── svc_hermes*.service          # Hermes daemon units
├── comfyui*.service
├── etf_backtest_strategy.py     # quant backtester
├── etf_sell_signals.py
├── etf_sell_orders_fixed.py
├── smart_pricing_engine.py      # eBay/Google parts pricing
├── ocr_tool.py / build_ocr_skill.py / ocr_skill_pkg/
├── copy_vault.py / stage_personas.py / stage_and_copy.py
├── *.sh / *.bat                 # ops + launchers
├── logo.jpg / logo.png
├── LICENSE
└── README.md
```

---

## Installation

> Requires Python 3.11+ on the operator workstation and a Linux fleet with
> NFS + systemd for the agent side.

```bash
# Operator workstation
git clone https://github.com/SparkSpheartech/NebulaForge.git
cd NebulaForge
pip install fpdf2 reportlab requests beautifulsoup4 pytesseract \
            easyocr pillow yfinance pandas numpy

# Agent VM (run as root during bring-up)
#   build_agents*.py provisions the VM, mounts the NFS share at
#   /sparksphear, installs Hermes, and drops agent_poll.py to
#   /usr/local/bin/agent_poll.py
#
# Enable the poller for a given agent user:
#   cp agent_poll.service /etc/systemd/system/agent_poll@.service
#   systemctl enable --now agent_poll@<agentname>
```

> **Note:** passwords and the NFS host/IP are placeholders in this public
> build (`REPLACE_WITH_YOUR_VM_PASSWORD`, `192.0.2.0/24`). Substitute your own
> infra values before deploying. Do **not** commit real credentials — they
> live in `*.b64` / agent token files that are git-ignored.

---

## Usage

```bash
# Dispatch a task to one agent
python delegate.py --to eissa \
  --title "TAM for HVAC leads in Fort Wayne" \
  --prompt "Research the TAM for residential HVAC in Fort Wayne IN and write
            a markdown summary to /sparksphear/03_Shared_Workspace/hvac_tam.md" \
  --skills research

# Broadcast to the whole fleet
python delegate.py --broadcast --title "Standup" --prompt "Post today's plan."

# Run the operator console
python SparkSphear_Main.py

# Run a trading backtest (writes sell_orders_ready.json)
python etf_backtest_strategy.py

# Query the pricing engine
python smart_pricing_engine.py
```

---

## Security Model

* **No secrets in source.** Tokens, bot credentials, and the NFS password are
  externalized to environment variables / `*.b64` files excluded by
  `.gitignore`. This public repo contains none of them.
* **`StrictHostKeyChecking=no`** appears in the ops scripts for lab
  convenience; in production, pin host keys and use SSH certificates.
* **Least-privilege agents.** Each agent runs as its own unprivileged user;
  `svc_hermes.service` drops privileges via `User=__USER__`.
* **Atomic task ownership** prevents double-execution races on the shared NFS.

---

## Roadmap

* [ ] Replace `sshpass`/password cloud-init with SSH cert auth.
* [ ] Add a Redis-backed fast-path bus alongside the NFS directory bus.
* [ ] Containerize the operator console for headless dispatch.
* [ ] Formalize the task schema with JSON Schema validation.
* [ ] Add Prometheus metrics for per-agent throughput/latency.

---

## License

[MIT](LICENSE) © 2026 Shazaly Musa / SparkSphear Tech Solutions.
