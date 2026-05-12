# n8n workflow

Set `FIM_WEBHOOK_URL` in the backend environment to your n8n webhook URL.

Recommended webhook payload fields:

```json
{
  "id": 1,
  "agent": "agent-001",
  "file": "C:/path/to/file.txt",
  "event": "file_modified",
  "severity": "medium",
  "time": 1778580000,
  "hash": "sha256-hash",
  "size": 1024
}
```

Use the `severity` field to route critical events differently from low-risk file creations.
