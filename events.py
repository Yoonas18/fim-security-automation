import asyncio
import json

# Max queue size prevents memory explosion
MAX_QUEUE_SIZE = 5000

# Shared async queue for SSE
events_queue = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)


async def push_event(data: dict):
    """
    Safely push new events into the SSE queue.
    If full, drop the oldest event to make space.
    """
    if events_queue.full():
        # drop oldest
        try:
            events_queue.get_nowait()
        except Exception:
            pass
    await events_queue.put(json.dumps(data))


async def event_stream(request):
    """
    Async generator for Server-Sent Events (SSE).
    Yields JSON-encoded events from the queue and keepalive comments.
    """
    keepalive_interval = 15

    while True:
        # Stop streaming if the client disconnects
        if await request.is_disconnected():
            break

        try:
            data = await asyncio.wait_for(events_queue.get(), timeout=keepalive_interval)
            yield f"data: {data}\n\n"
        except asyncio.TimeoutError:
            # keep connection alive for proxies / browsers
            yield ": keep-alive\n\n"
        except asyncio.CancelledError:
            break
