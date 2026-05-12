# FIM Security Watchdog

A defensive File Integrity Monitoring platform with a Python agent, FastAPI event collector, authenticated dashboard, SQLite event history, and optional n8n alert forwarding.

This project is built for learning and portfolio demonstration, but the core flow mirrors real host-based detection work: an agent hashes files, detects changes, sends structured events to a server, and the dashboard shows live security activity.

## Features

- SHA-256 file integrity monitoring
- Detection for created, modified, and deleted files
- Agent API key protection
- Authenticated web dashboard
- Live Server-Sent Events alert stream
- SQLite event history
- Filtering by agent and event type
- Severity labels for suspicious or sensitive paths
- Optional n8n webhook forwarding
- Safe config examples so secrets are not committed

## Project structure

```text
fim-security-automation/
  agent/
    agent.py
    agent_config.example.json
  backend/
    __init__.py
    database.py
    events.py
    main.py
    schemas.py
  frontend/
    index.html
  n8n-workflows/
    README.md
  .env.example
  .gitignore
  LICENSE
  README.md
  requirements.txt
```

## Quick start

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Set environment variables. You can copy `.env.example` into your shell or use your preferred environment manager.

Important values:

```text
FIM_ADMIN_USERNAME=admin
FIM_ADMIN_PASSWORD=change-this-dashboard-password
FIM_SESSION_SECRET=change-this-long-random-session-secret
FIM_AGENT_API_KEY=change-this-agent-api-key
FIM_WEBHOOK_URL=
```

Start the backend from the repository root:

```bash
uvicorn backend.main:app --reload --port 8000
```

Open the dashboard:

```text
http://127.0.0.1:8000
```

## Agent setup

Copy the example config:

```bash
copy agent\agent_config.example.json agent\agent_config.json
```

Edit `agent/agent_config.json`:

```json
{
  "agent_id": "agent-001",
  "backend_url": "http://127.0.0.1:8000/api/report",
  "api_key": "change-this-agent-api-key",
  "watch_paths": ["C:/path/to/monitor"],
  "scan_interval_seconds": 5,
  "max_file_size_mb": 100,
  "ignore_names": [".git", "__pycache__", "node_modules", ".venv"]
}
```

Run the agent:

```bash
python agent\agent.py
```

## API overview

Dashboard endpoints require the login session cookie:

- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `GET /api/history`
- `GET /api/stats`
- `GET /api/events`

Agent reporting requires the `X-Agent-Key` header:

```http
POST /api/report
X-Agent-Key: change-this-agent-api-key
```

Example payload:

```json
{
  "agent_id": "agent-001",
  "file": "C:/important/config.txt",
  "event": "file_modified",
  "hash": "sha256-hash",
  "size": 1024
}
```

## Security notes

- Change all default secrets before using the project outside a local demo.
- Keep `.env`, `agent/agent_config.json`, and database files out of Git.
- Use HTTPS or a trusted private network if agents report to a remote backend.
- Monitor only systems and folders you own or have explicit permission to monitor.
- This project is for defensive security education and authorized monitoring.

## Author

Yoonus K Y

