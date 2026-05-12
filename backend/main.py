import hmac
import os
import secrets
import time
from pathlib import Path
from typing import Annotated

import httpx
from fastapi import Cookie, Depends, FastAPI, Header, HTTPException, Query, Request, Response, status
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from .database import get_events, get_stats, init_db, save_event
from .events import event_stream, push_event
from .schemas import LoginRequest, Report


APP_NAME = "FIM Security Watchdog"
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
SESSION_COOKIE = "fim_session"
SESSION_TTL_SECONDS = int(os.getenv("FIM_SESSION_TTL_SECONDS", "28800"))

ADMIN_USERNAME = os.getenv("FIM_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("FIM_ADMIN_PASSWORD", "change-me")
SESSION_SECRET = os.getenv("FIM_SESSION_SECRET", "dev-session-secret-change-me")
AGENT_API_KEY = os.getenv("FIM_AGENT_API_KEY", "change-me-agent-key")
WEBHOOK_URL = os.getenv("FIM_WEBHOOK_URL", "").strip()


app = FastAPI(title=APP_NAME)
init_db()


def _sign(value: str) -> str:
    return hmac.new(SESSION_SECRET.encode(), value.encode(), "sha256").hexdigest()


def create_session() -> str:
    expires = int(time.time()) + SESSION_TTL_SECONDS
    nonce = secrets.token_urlsafe(24)
    value = f"{expires}.{nonce}"
    return f"{value}.{_sign(value)}"


def require_dashboard_auth(fim_session: Annotated[str | None, Cookie()] = None) -> None:
    if not fim_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    try:
        expires_text, nonce, signature = fim_session.split(".", 2)
        value = f"{expires_text}.{nonce}"
        expires = int(expires_text)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    if expires < int(time.time()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    if not hmac.compare_digest(signature, _sign(value)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")


def require_agent_key(x_agent_key: Annotated[str | None, Header()] = None) -> None:
    if not x_agent_key or not hmac.compare_digest(x_agent_key, AGENT_API_KEY):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid agent API key")


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": APP_NAME}


@app.post("/api/auth/login")
async def login(payload: LoginRequest, response: Response):
    valid_user = hmac.compare_digest(payload.username, ADMIN_USERNAME)
    valid_password = hmac.compare_digest(payload.password, ADMIN_PASSWORD)

    if not valid_user or not valid_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    response.set_cookie(
        SESSION_COOKIE,
        create_session(),
        httponly=True,
        samesite="lax",
        max_age=SESSION_TTL_SECONDS,
    )
    return {"status": "ok"}


@app.post("/api/auth/logout")
async def logout(response: Response):
    response.delete_cookie(SESSION_COOKIE)
    return {"status": "ok"}


@app.get("/api/auth/me")
async def me(_: Annotated[None, Depends(require_dashboard_auth)]):
    return {"username": ADMIN_USERNAME}


@app.post("/api/report")
async def report(data: Report, _: Annotated[None, Depends(require_agent_key)]):
    event = save_event(data.agent_id, data.file, data.event, data.hash, data.size)
    await push_event(event)

    if WEBHOOK_URL:
        async with httpx.AsyncClient(timeout=5) as client:
            try:
                await client.post(WEBHOOK_URL, json=event)
            except httpx.HTTPError as exc:
                print("[webhook error]", exc)

    return {"status": "ok", "event_id": event["id"]}


@app.get("/api/events")
async def sse(request: Request, _: Annotated[None, Depends(require_dashboard_auth)]):
    return StreamingResponse(event_stream(request), media_type="text/event-stream")


@app.get("/api/history")
async def history(
    _: Annotated[None, Depends(require_dashboard_auth)],
    limit: int = Query(default=200, ge=1, le=500),
    event: str | None = Query(default=None),
    agent: str | None = Query(default=None),
):
    return get_events(limit=limit, event=event, agent=agent)


@app.get("/api/stats")
async def stats(_: Annotated[None, Depends(require_dashboard_auth)]):
    return get_stats()


if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
