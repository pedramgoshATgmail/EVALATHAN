"""Local Hydra desk: ui/v2 files on this PC, shown in an Evalathan desktop window."""

from __future__ import annotations

import json
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from evalathan.desk import prepare
from evalathan.desk_store import load_run_sets, runs_path, save_run_sets, state_dir
from evalathan.hydra import conduct
from evalathan.launch_splash import request_close as close_launch_splash
from evalathan.launch_splash import spawn_if_needed as spawn_launch_splash

PORT = 8787


def ui_root() -> Path:
    """Repo ui/v2 when editable; falls back beside this file's parents."""
    here = Path(__file__).resolve()
    candidate = here.parents[2] / "ui" / "v2"
    if (candidate / "index.html").is_file():
        return candidate
    raise FileNotFoundError(
        "ui/v2 was not found. Run from an Evalathan checkout with ui/v2 present."
    )


def app_icon() -> Path | None:
    icon = ui_root() / "assets" / "favicon.ico"
    return icon if icon.is_file() else None


class DeskHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory: str | None = None, **kwargs):
        super().__init__(*args, directory=directory or str(ui_root()), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.end_headers()

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError as exc:
            raise ValueError("Request body must be JSON.") from exc
        if not isinstance(data, dict):
            raise ValueError("Request body must be a JSON object.")
        return data

    def _send_json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/runs":
            try:
                sets = load_run_sets()
                self._send_json(
                    200,
                    {
                        "ok": True,
                        "runSets": sets,
                        "path": str(runs_path()),
                    },
                )
            except Exception as exc:  # noqa: BLE001
                self._send_json(
                    500, {"ok": False, "error": str(exc) or exc.__class__.__name__}
                )
            return
        return super().do_GET()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            if path == "/api/evaluate":
                self._evaluate()
                return
            if path == "/api/pick-folder":
                self._pick_folder()
                return
            if path == "/api/runs":
                self._save_runs()
                return
            if path == "/api/download-memo":
                self._download_memo()
                return
            self._send_json(404, {"ok": False, "error": "Unknown API route."})
        except ValueError as exc:
            self._send_json(400, {"ok": False, "error": str(exc) or "Bad request."})
        except Exception as exc:  # noqa: BLE001 - return message to the desk
            self._send_json(500, {"ok": False, "error": str(exc) or exc.__class__.__name__})

    def _save_runs(self) -> None:
        data = self._read_json()
        run_sets = data.get("runSets")
        if not isinstance(run_sets, list):
            raise ValueError("Body must include a runSets array.")
        path = save_run_sets(run_sets)
        self._send_json(200, {"ok": True, "path": str(path), "count": len(run_sets)})

    def _download_memo(self) -> None:
        """Write memo PDF (or HTML fallback) straight to Downloads - no print dialog."""
        from evalathan.memo_download import save_memo_download

        data = self._read_json()
        html = str(data.get("html") or "")
        name = str(data.get("filename") or data.get("suggestedName") or "Evalathan-memo")
        result = save_memo_download(html, name)
        code = 200 if result.get("ok") else 500
        self._send_json(code, result)

    def _evaluate(self) -> None:
        data = self._read_json()
        target = str(data.get("target") or "").strip()
        if not target:
            raise ValueError("Paste a GitHub link or a folder on this PC.")
        folder, note = prepare(target)
        report = conduct(folder)
        payload = {
            "ok": True,
            "note": note or "",
            "target": target,
            "folder": str(folder),
            "report": report.to_dict(),
            "render": report.render(),
        }
        self._send_json(200, payload)

    def _pick_folder(self) -> None:
        """Native folder dialog on this machine (same role as Tk Browse)."""
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        try:
            chosen = filedialog.askdirectory(title="Choose the software folder")
        finally:
            root.destroy()
        if not chosen:
            self._send_json(200, {"ok": True, "path": "", "cancelled": True})
            return
        self._send_json(200, {"ok": True, "path": chosen, "cancelled": False})

    def log_message(self, fmt: str, *args) -> None:
        sys_stderr = __import__("sys").stderr
        sys_stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def start_server(port: int = PORT) -> ThreadingHTTPServer:
    import mimetypes

    mimetypes.add_type("image/webp", ".webp")
    mimetypes.add_type("image/webp", ".WEBP")
    httpd = ThreadingHTTPServer(("127.0.0.1", port), DeskHandler)
    return httpd


def _open_desktop_window(url: str, title: str) -> bool:
    """Show the local desk in a native window with the Evalathan title (no browser chrome)."""
    try:
        import webbrowser

        import webview
    except ImportError:
        close_launch_splash()
        return False

    class DeskBridge:
        """JS bridge so GLOSS / SELFBELT / glossary links open in the real browser.

        On macOS, window.open() from the desk WebView is often a no-op. target=_blank
        links need OPEN_EXTERNAL_LINKS_IN_BROWSER; this bridge covers button clicks too.
        """

        def open_external(self, href: str) -> bool:
            target = (href or "").strip()
            if not target:
                return False
            webbrowser.open(target)
            return True

        def save_memo_download(self, html: str, suggested_name: str = "Evalathan-memo") -> dict:
            from evalathan.memo_download import save_memo_download as _save

            return _save(html or "", suggested_name or "Evalathan-memo")

    icon = app_icon()
    kwargs = {
        "title": title,
        "url": url,
        "width": 1440,
        "height": 900,
        "min_size": (960, 640),
        "js_api": DeskBridge(),
    }
    # Drop the FUSS launching splash once the real desk window is ready.
    close_launch_splash()
    try:
        webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = True
    except Exception:  # noqa: BLE001
        pass
    try:
        if icon is not None:
            webview.create_window(**kwargs, icon=str(icon))
        else:
            webview.create_window(**kwargs)
    except TypeError:
        kwargs.pop("js_api", None)
        try:
            if icon is not None:
                webview.create_window(**kwargs, icon=str(icon))
            else:
                webview.create_window(**kwargs)
        except TypeError:
            webview.create_window(
                title=title, url=url, width=1440, height=900, min_size=(960, 640)
            )
    # private_mode=True (pywebview default on some builds) wipes localStorage on close.
    storage = state_dir() / "webview"
    storage.mkdir(parents=True, exist_ok=True)
    try:
        webview.start(private_mode=False, storage_path=str(storage))
    except TypeError:
        try:
            webview.start(private_mode=False)
        except TypeError:
            webview.start()
    return True

def open_desk(port: int = PORT, open_window: bool = True) -> int:
    """Serve ui/v2 from this PC and open the Evalathan desktop window."""
    # Global update ask: if GitHub main is ahead, popup Update now / Not now.
    try:
        from evalathan.desk_update import ensure_published_main

        ensure_published_main(interactive=True)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001
        print(f"Evalathan update check skipped: {exc}", flush=True)

    root = ui_root()
    try:
        from evalathan import __version__ as ver
    except Exception:  # noqa: BLE001
        ver = "0.3.2"
    # Keep or start the centered FUSS "launching..." splash until the desk window opens.
    spawn_launch_splash()
    httpd = None
    bound = port
    last_err: Exception | None = None
    for candidate in range(port, port + 8):
        try:
            httpd = start_server(candidate)
            bound = candidate
            break
        except OSError as exc:
            last_err = exc
            continue
    if httpd is None:
        close_launch_splash()
        raise RuntimeError(
            f"Could not bind a local desk port starting at {port}: {last_err}"
        ) from last_err
    # Loopback only. All UI files live under ui/v2 on this machine.
    url = f"http://127.0.0.1:{bound}/"
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    print(f"Evalathan v{ver} local desk", flush=True)
    print(f"Installed files: {root}", flush=True)
    print("Opening the Evalathan desktop window (dragon icon on your Desktop)...", flush=True)
    try:
        if open_window:
            if not _open_desktop_window(url, f"EVALATHAN v{ver}"):
                import webbrowser

                print(
                    "Install tip: pywebview is required for the desktop window.",
                    flush=True,
                )
                close_launch_splash()
                webbrowser.open(url)
                thread.join()
        else:
            close_launch_splash()
            thread.join()
    except KeyboardInterrupt:
        pass
    finally:
        close_launch_splash()
        httpd.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(open_desk())
