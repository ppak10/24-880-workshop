"""Directory and file path constants for the workshop-extension GUI."""

from pathlib import Path

# Built React bundle — populated by `npm run build` in gui/web/.
GUI_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "gui"

# Runtime state directory (PID file, etc.).
_STATE_DIR = Path.home() / ".workshop-extension"
PID_FILE = _STATE_DIR / "gui.pid"
