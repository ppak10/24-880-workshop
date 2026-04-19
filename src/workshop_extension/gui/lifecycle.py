"""Start/stop the workshop-extension GUI server subprocess."""

import os
import signal
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

from workshop_extension.gui.layout import PID_FILE
from workshop_extension.gui.server import DEFAULT_HOST, DEFAULT_PORT


# ── Process / port helpers ────────────────────────────────────────────────────


def _is_pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _is_port_in_use(port: int, host: str = DEFAULT_HOST) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, port))
            return False
        except OSError:
            return True


def _read_pid_file() -> list[int]:
    if not PID_FILE.is_file():
        return []
    try:
        text = PID_FILE.read_text().strip()
        return [int(line) for line in text.splitlines() if line.strip().isdigit()]
    except (OSError, ValueError):
        return []


def _kill_pid(pid: int) -> bool:
    if pid == os.getpid():
        return False
    try:
        os.kill(pid, signal.SIGTERM)
        return True
    except (ProcessLookupError, PermissionError, OSError):
        return False


def _check_existing() -> str:
    """Return 'healthy', 'stale', 'port_conflict', or 'none'."""
    pids = _read_pid_file()
    port_busy = _is_port_in_use(DEFAULT_PORT, DEFAULT_HOST)

    if not pids:
        return "port_conflict" if port_busy else "none"

    if all(_is_pid_alive(p) for p in pids) and port_busy:
        return "healthy"

    for p in pids:
        _kill_pid(p)
    try:
        PID_FILE.unlink(missing_ok=True)
    except OSError:
        pass
    return "port_conflict" if _is_port_in_use(DEFAULT_PORT, DEFAULT_HOST) else "stale"


# ── Public lifecycle API ──────────────────────────────────────────────────────


def start_gui_server(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
) -> dict:
    """Launch the GUI server and open the browser.

    Returns a status dict with keys:
        pid (int | None), server_url (str | None), reused (bool), error (str | None)

    Never raises — failures are returned via the ``error`` key.
    """
    state = _check_existing()

    if state == "healthy":
        pids = _read_pid_file()
        return {
            "pid": pids[0] if pids else None,
            "server_url": f"http://{host}:{port}",
            "reused": True,
            "error": None,
        }

    if state == "port_conflict":
        return {
            "pid": None,
            "server_url": None,
            "reused": False,
            "error": f"Port {port} is already in use by another process.",
        }

    from workshop_extension.gui.layout import GUI_DATA_DIR

    if not GUI_DATA_DIR.is_dir():
        return {
            "pid": None,
            "server_url": None,
            "reused": False,
            "error": (
                f"GUI build output not found at {GUI_DATA_DIR}. "
                "Run 'npm run build' inside src/workshop_extension/gui/web/ first."
            ),
        }

    cmd = [
        sys.executable,
        "-c",
        (
            "from workshop_extension.gui.server import run; "
            f"run(host={host!r}, port={port})"
        ),
    ]
    try:
        proc = subprocess.Popen(
            cmd,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        return {
            "pid": None,
            "server_url": None,
            "reused": False,
            "error": f"Failed to launch server: {e}",
        }

    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(proc.pid))

    time.sleep(0.8)
    webbrowser.open(f"http://{host}:{port}")

    return {
        "pid": proc.pid,
        "server_url": f"http://{host}:{port}",
        "reused": False,
        "error": None,
    }


def stop_gui_server() -> list[int]:
    """Kill all GUI server processes. Returns the PIDs that were signalled."""
    pids = _read_pid_file()
    killed = [p for p in pids if _kill_pid(p)]
    try:
        PID_FILE.unlink(missing_ok=True)
    except OSError:
        pass
    return killed
