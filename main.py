from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from database import init_db, save_event, get_events
from events import events_queue, event_stream, push_event
import json
import httpx
import os

app = FastAPI()
init_db()

WEBHOOK_URL = "n8n webhook url"


@app.post("/api/report")
async def report(data: dict):
    agent = data.get("agent_id")
    file_path = data.get("file")
    event = data.get("event")

    save_event(agent, file_path, event)

    await push_event({
        "agent": agent,
        "file": file_path,
        "event": event,
        "time": None
    })

    async with httpx.AsyncClient(timeout=5) as client:
        try:
            await client.post(WEBHOOK_URL, json=data)
        except Exception as e:
            print("[n8n ERROR]", e)

    return {"status": "ok"}


@app.get("/api/events")
async def sse(request: Request):
    return StreamingResponse(
        event_stream(request),
        media_type="text/event-stream"
    )


@app.get("/api/history")
async def history():
    return get_events()


# --------------------------------------------------
# THIS MUST BE LAST — DO NOT MOVE ABOVE API ROUTES
# --------------------------------------------------
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
