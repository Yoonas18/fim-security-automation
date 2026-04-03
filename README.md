# 🔍 FIM & Security Automation Platform

> A Python-based File Integrity Monitoring system with real-time alerting, centralized event collection, and n8n-powered security automation workflows.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![n8n](https://img.shields.io/badge/n8n-EA4B71?style=flat&logo=n8n&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Security](https://img.shields.io/badge/Security-Tool-red?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

---

## 📌 Overview

This project simulates a real-world **File Integrity Monitoring (FIM)** system — the kind used in enterprise SOC environments to detect unauthorized changes to critical files. It uses **SHA-256 hashing** to baseline files and continuously monitors for modifications, deletions, or new file creations. When a change is detected, automated workflows trigger **instant Telegram alerts** via **n8n**.

This is a practical demonstration of:
- Host-based intrusion detection concepts
- Security automation using n8n workflows
- SOC-style event collection and alerting
- Python security tool development

---

## 🏗 Architecture

```
┌─────────────────────┐     events      ┌──────────────────┐
│   FIM Monitor       │ ─────────────▶  │  FastAPI Server  │
│  (Python agent)     │                 │  (Event Collector)│
│                     │                 └────────┬─────────┘
│  • SHA-256 hashing  │                          │
│  • Baseline compare │                          ▼
│  • Change detection │                 ┌──────────────────┐
└─────────────────────┘                 │   n8n Workflow   │
                                        │  (Automation)    │
                                        │                  │
                                        │  • Parse event   │
                                        │  • Format alert  │
                                        │  • Send Telegram │
                                        └──────────────────┘
```

---

## ✨ Features

- ✅ **SHA-256 file hashing** — cryptographically detects any file modification
- ✅ **Real-time monitoring** — continuously watches specified directories
- ✅ **Baseline management** — create, store, and compare file hash baselines
- ✅ **Change detection** — detects file modifications, new files, and deletions
- ✅ **Centralized event collection** — FastAPI server collects events from the monitoring agent
- ✅ **Automated alerting** — n8n workflow sends instant Telegram notifications
- ✅ **Structured logging** — all events stored with timestamps for investigation

---

## 🛠 Tech stack

| Component | Technology |
|-----------|------------|
| Monitoring agent | Python 3 |
| Event collector API | FastAPI |
| Automation workflows | n8n |
| Alert channel | Telegram Bot |
| Hash algorithm | SHA-256 |

---

## 📁 Project structure

```
FIM-Watchdog/
├── agent/
│   ├── agent.py                  ← improved with better error messages & comments
│   ├── agent_config.json         ← safe generic paths (your Desktop path removed)
│   └── agent_config.example.json ← template for other users
├── backend/
│   ├── main.py                   ← webhook moved to env variable (no hardcoded URL)
│   ├── database.py               ← unchanged (was already clean)
│   ├── events.py                 ← unchanged
│   └── schemas.py                ← unchanged
├── frontend/
│   └── index.html                ← unchanged (your UI is great)
├── docs/
│   └── SCREENSHOTS.md            ← guide for what screenshots to add
├── README.md                     ← full professional README
├── requirements.txt              ← all dependencies listed
├── .gitignore                    ← blocks .db files, __pycache__, config
├── .env.example                  ← shows how to set N8N_WEBHOOK_URL safely
└── LICENSE                       ← MIT license

## 🚀 Getting started

### Prerequisites

- Python 3.8+
- n8n (self-hosted or cloud)
- Telegram Bot Token ([create one via @BotFather](https://t.me/botfather))

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Yoonas18/fim-security-automation.git
cd fim-security-automation

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure monitored paths
nano agent/config.py
# Set MONITOR_PATHS = ["/path/to/watch"]
# Set API_URL = "http://localhost:8000"

# 4. Start the event collection server
uvicorn server.main:app --reload --port 8000

# 5. Create the initial baseline
python agent/baseline.py --create

# 6. Start the FIM monitor
python agent/fim_monitor.py
```

### n8n workflow setup

1. Open your n8n instance
2. Go to **Workflows → Import**
3. Import `n8n-workflows/fim_alert_workflow.json`
4. Add your Telegram Bot Token and Chat ID in the Telegram node
5. Activate the workflow

---

## 📸 How it works

### 1. Baseline creation
The agent scans all monitored directories and stores SHA-256 hashes of every file:
```
[INFO] Baseline created: 47 files hashed
[INFO] Baseline saved to: baseline.json
```

### 2. Continuous monitoring
The agent re-hashes files at set intervals and compares against the baseline:
```
[ALERT] MODIFIED  → /etc/passwd  (hash mismatch)
[ALERT] NEW FILE  → /tmp/suspicious.sh
[INFO]  UNCHANGED → /var/log/syslog
```

### 3. Event sent to FastAPI server
```json
{
  "event_type": "MODIFIED",
  "file_path": "/etc/passwd",
  "old_hash": "a3f5c...",
  "new_hash": "9b2d1...",
  "timestamp": "2025-08-14T10:32:11Z"
}
```

### 4. n8n triggers Telegram alert
```
🚨 FIM ALERT
Type: File Modified
Path: /etc/passwd
Time: 2025-08-14 10:32:11
Hash changed — investigate immediately!
```

---

## 🔒 Security use cases

This tool demonstrates detection of:
- Unauthorized modification of system files (e.g. `/etc/passwd`, `/etc/sudoers`)
- Web shell uploads to web server directories
- Persistence mechanisms that drop files on disk
- Configuration tampering by insiders or malware

---

## 📚 Learning outcomes

By building and running this project you gain practical experience with:
- Host-based intrusion detection (HIDS) concepts
- Cryptographic file integrity verification
- RESTful API design for security event collection
- Security automation and alerting workflows
- Incident response data collection

---

## 🙋 Author

**Yoonus K Y** — Cybersecurity Researcher & Penetration Tester

[![Portfolio](https://img.shields.io/badge/Portfolio-1B3A6B?style=flat&logo=githubpages&logoColor=white)](https://yoonas18.github.io/portfolio)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/yoonusky)
[![Bugcrowd](https://img.shields.io/badge/Bugcrowd-F26822?style=flat&logo=bugcrowd&logoColor=white)](https://bugcrowd.com/Yoonas18)

---

## ⚠️ Disclaimer

This tool is built for **educational and defensive security purposes only**. Only monitor systems you own or have explicit written permission to monitor.
