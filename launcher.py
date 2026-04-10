"""
PyInstaller entry point for Salary Manager.
Sets path environment variables before importing any app modules,
then launches the FastAPI server and opens the browser.
"""
import sys
import os
import threading
import webbrowser
import time

# ── Resolve paths ─────────────────────────────────────────────────────────────

if getattr(sys, "frozen", False):
    # Running inside a PyInstaller bundle
    _BUNDLE_DIR = sys._MEIPASS                        # bundled files (read-only)
    _DATA_DIR   = os.path.dirname(sys.executable)     # next to the .exe (writable)
else:
    _BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))
    _DATA_DIR   = _BUNDLE_DIR

# Expose to backend modules via environment variables
os.environ["SM_BUNDLE_DIR"] = _BUNDLE_DIR
os.environ["SM_DATA_DIR"]   = _DATA_DIR

# Add bundled backend to import path
sys.path.insert(0, os.path.join(_BUNDLE_DIR, "backend"))

# ── Fix stdout/stderr for windowed (console=False) PyInstaller builds ─────────
# When built with console=False, sys.stdout and sys.stderr are None.
# Uvicorn's DefaultFormatter calls stream.isatty() during logging config,
# which raises AttributeError on None. Redirect to a log file to fix this.

if getattr(sys, "frozen", False) and sys.stdout is None:
    _log_path = os.path.join(_DATA_DIR, "salary-manager.log")
    _log_file = open(_log_path, "a", encoding="utf-8", buffering=1)
    sys.stdout = _log_file
    sys.stderr = _log_file

# ── Launch ────────────────────────────────────────────────────────────────────

import uvicorn  # noqa: E402  (must come after sys.path update)

PORT = 8080


def _open_browser():
    time.sleep(1.5)
    webbrowser.open(f"http://localhost:{PORT}")


if __name__ == "__main__":
    threading.Thread(target=_open_browser, daemon=True).start()
    # log_config=None disables uvicorn's logging setup entirely,
    # avoiding any further formatter/stream issues in the frozen exe.
    uvicorn.run("main:app", host="127.0.0.1", port=PORT, log_config=None)
