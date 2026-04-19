"""aiohttp backend: weather API + WebSocket push + static file server."""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from aiohttp import web, WSMsgType

from workshop_extension.gui.layout import GUI_DATA_DIR

logger = logging.getLogger(__name__)

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 24880
REFRESH_INTERVAL = 300  # seconds (5 minutes)


# ── Weather fetching ──────────────────────────────────────────────────────────


def _fetch_weather_sync() -> dict:
    """Blocking call to Open-Meteo — run in a thread executor."""
    from workshop_extension.weather.client import umbrella_summary

    data = umbrella_summary("Pittsburgh, PA")
    data["updated_at"] = datetime.now().isoformat()
    return data


# ── WebSocket handler ─────────────────────────────────────────────────────────


async def _ws_handler(request: web.Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    request.app["clients"].add(ws)

    # Send cached weather immediately on connect.
    cached = request.app.get("weather")
    if cached is not None:
        await ws.send_str(json.dumps({"type": "weather", "data": cached}))

    try:
        async for msg in ws:
            if msg.type in (WSMsgType.ERROR, WSMsgType.CLOSE):
                break
    finally:
        request.app["clients"].discard(ws)

    return ws


# ── REST handlers ─────────────────────────────────────────────────────────────


async def _weather_handler(request: web.Request) -> web.Response:
    data = request.app.get("weather")
    if data is None:
        return web.json_response({"error": "Weather data not yet available."}, status=503)
    return web.json_response(data)


# ── Background refresh loop ───────────────────────────────────────────────────


async def _refresh_loop(app: web.Application) -> None:
    loop = asyncio.get_event_loop()
    while True:
        try:
            data = await loop.run_in_executor(None, _fetch_weather_sync)
            app["weather"] = data
            msg = json.dumps({"type": "weather", "data": data})
            for ws in list(app["clients"]):
                try:
                    await ws.send_str(msg)
                except Exception:
                    app["clients"].discard(ws)
        except Exception as exc:
            logger.warning("Weather refresh failed: %s", exc)
        await asyncio.sleep(REFRESH_INTERVAL)


# ── App factory ───────────────────────────────────────────────────────────────


async def _on_startup(app: web.Application) -> None:
    # Prime the cache before the first WebSocket connection.
    loop = asyncio.get_event_loop()
    try:
        app["weather"] = await loop.run_in_executor(None, _fetch_weather_sync)
    except Exception as exc:
        logger.warning("Initial weather fetch failed: %s", exc)
        app["weather"] = None

    app["refresh_task"] = asyncio.create_task(_refresh_loop(app))


async def _on_cleanup(app: web.Application) -> None:
    task = app.get("refresh_task")
    if task:
        task.cancel()
    for ws in list(app.get("clients", [])):
        await ws.close()


def build_app() -> web.Application:
    app = web.Application()
    app["clients"]: set = set()
    app["weather"] = None

    app.on_startup.append(_on_startup)
    app.on_cleanup.append(_on_cleanup)

    app.router.add_get("/ws", _ws_handler)
    app.router.add_get("/api/weather", _weather_handler)

    # Serve the built React bundle.
    if GUI_DATA_DIR.is_dir():
        assets_dir = GUI_DATA_DIR / "assets"
        if assets_dir.is_dir():
            app.router.add_static("/assets", assets_dir, name="assets")

        async def _main_js(_request: web.Request) -> web.FileResponse:
            return web.FileResponse(GUI_DATA_DIR / "main.js")

        async def _index(_request: web.Request) -> web.FileResponse:
            return web.FileResponse(GUI_DATA_DIR / "index.html")

        app.router.add_get("/main.js", _main_js)
        app.router.add_get("/", _index)
        app.router.add_get("/{path:.*}", _index)

    return app


def run(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    """Entry point called by lifecycle subprocess."""
    logging.basicConfig(level=logging.WARNING)
    app = build_app()
    web.run_app(app, host=host, port=port, access_log=None)
