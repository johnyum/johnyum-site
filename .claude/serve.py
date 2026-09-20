#!/usr/bin/env python3
"""Static dev server for the site.

Serves the repo root on $PORT (the harness assigns one; 4173 if unset), so two
chats can preview at once instead of fighting over a hardcoded port. The root is
derived from this file's own location, not the cwd — the sandbox does not always
hand us a readable one.
"""
import functools
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(os.environ.get("PORT") or 4173)

handler = functools.partial(SimpleHTTPRequestHandler, directory=ROOT)
httpd = ThreadingHTTPServer(("127.0.0.1", PORT), handler)
print(f"serving {ROOT} on http://127.0.0.1:{PORT}", flush=True)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    sys.exit(0)
