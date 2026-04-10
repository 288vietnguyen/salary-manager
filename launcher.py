"""
PyInstaller entry point for Salary Manager.
Sets path environment variables before importing any app modules,
then launches the FastAPI server and opens the browser.
Shows a system tray icon so the user can Quit the server from Windows.
"""
import sys
import os
import threading
import webbrowser
import asyncio

# ── Fix stdout/stderr for windowed (console=False) PyInstaller builds ─────────
# When built with console=False, sys.stdout and sys.stderr are None.
# Uvicorn's DefaultFormatter calls stream.isatty() during logging config,
# which raises AttributeError on None. Redirect to a log file to fix this.

if getattr(sys, "frozen", False) and sys.stdout is None:
    _log_path = os.path.join(os.path.dirname(sys.executable), "salary-manager.log")
    _log_file = open(_log_path, "a", encoding="utf-8", buffering=1)
    sys.stdout = _log_file
    sys.stderr = _log_file

# ── Resolve paths ─────────────────────────────────────────────────────────────

if getattr(sys, "frozen", False):
    _BUNDLE_DIR = sys._MEIPASS                        # bundled files (read-only)
    _DATA_DIR   = os.path.dirname(sys.executable)     # next to the .exe (writable)
else:
    _BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))
    _DATA_DIR   = _BUNDLE_DIR

os.environ["SM_BUNDLE_DIR"] = _BUNDLE_DIR
os.environ["SM_DATA_DIR"]   = _DATA_DIR
sys.path.insert(0, os.path.join(_BUNDLE_DIR, "backend"))

# ── Server ────────────────────────────────────────────────────────────────────

import uvicorn  # noqa: E402

PORT    = 8080
_server: uvicorn.Server | None = None


def _run_server():
    global _server
    config  = uvicorn.Config("main:app", host="127.0.0.1", port=PORT, log_config=None)
    _server = uvicorn.Server(config)
    asyncio.run(_server.serve())


def _open_browser():
    import time
    time.sleep(1.5)
    webbrowser.open(f"http://localhost:{PORT}")


# ── Tray icon ─────────────────────────────────────────────────────────────────

def _make_tray_icon():
    """Generate a simple coloured circle icon with PIL."""
    from PIL import Image, ImageDraw
    size = 64
    img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d    = ImageDraw.Draw(img)
    # Indigo circle
    d.ellipse([2, 2, size - 2, size - 2], fill=(99, 102, 241))
    # Dollar sign
    d.text((21, 14), "$", fill="white")
    return img


def _quit_app(icon, _item):
    global _server
    icon.stop()
    if _server:
        _server.should_exit = True


def _open_app(_icon=None, _item=None):
    webbrowser.open(f"http://localhost:{PORT}")


def _run_tray():
    try:
        import pystray
        icon = pystray.Icon(
            "SalaryManager",
            _make_tray_icon(),
            "Salary Manager",
            menu=pystray.Menu(
                pystray.MenuItem("Open", _open_app, default=True),
                pystray.MenuItem("Quit", _quit_app),
            ),
        )
        icon.run()  # blocks until icon.stop() is called
    except Exception as e:
        print(f"[tray] {e}", flush=True)


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if getattr(sys, "frozen", False):
        # Running as .exe — server in background, tray on main thread
        server_thread = threading.Thread(target=_run_server, daemon=True)
        server_thread.start()

        threading.Thread(target=_open_browser, daemon=True).start()

        # Tray blocks until user clicks Quit
        _run_tray()

        if _server:
            _server.should_exit = True
        server_thread.join(timeout=5)
    else:
        # Running locally — uvicorn on main thread, stop with Ctrl+C
        threading.Thread(target=_open_browser, daemon=True).start()
        _run_server()
