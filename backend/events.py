import asyncio
import json
from typing import Any


MAX_QUEUE_SIZE = 5000
events_queue: asyncio.Queue[str] = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)


async def push_event(data: dict[str, Any]) -> None:
    if events_queue.full():
        try:
            events_queue.get_nowait()
        except asyncio.QueueEmpty:
            pass

    await events_queue.put(json.dumps(data))


async def event_stream(request):
    keepalive_interval = 15

    while True:
        if await request.is_disconnected():
            break

        try:
            data = await asyncio.wait_for(events_queue.get(), timeout=keepalive_interval)
            yield f"data: {data}\n\n"
        except asyncio.TimeoutError:
            yield ": keep-alive\n\n"
        except asyncio.CancelledError:
            break
