"""Serve the prototype on http://localhost:8767 and tell the browser never to keep a copy.

Python's plain http.server sends no cache rule, so a browser may show an old stylesheet or
script after a file changes. This server adds "Cache-Control: no-store" to every reply.
Run it from the repo root: python3 prototype/serve.py
"""

import functools
import http.server
from pathlib import Path

PORT = 8767


class NoStoreHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    handler = functools.partial(NoStoreHandler, directory=str(Path(__file__).parent))
    http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler).serve_forever()
