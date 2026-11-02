"""Serve Evalathan UI v2 with correct WebP MIME (stdlib http.server alone maps .webp poorly)."""
from __future__ import annotations

import mimetypes
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PORT = 8787

mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("image/webp", ".WEBP")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()


if __name__ == "__main__":
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Evalathan ui/v2 on http://127.0.0.1:{PORT}/", flush=True)
    httpd.serve_forever()
