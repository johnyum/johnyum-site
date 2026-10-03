#!/usr/bin/env python3
"""Monsters — the local half of the sketch-to-monster pipeline.

johnyum.com/monsters runs on api/monsters.py (a Vercel function, passcode-gated).
This is the same thing on your Mac: it serves the repo as static files and
answers the same /api/monsters route, using that file's Meshy helpers — so
there is one copy of the proxy, not two. Run from anywhere:

    python3 monsters/serve.py            # then open http://127.0.0.1:5320/monsters/

What only the local one does:
  - no passcode and no daily cap — it's your machine
  - the key comes from MESHY_API_KEY or monsters/.env (gitignored), and the
    page's key box can write that file (p=key)
  - MOCK mode with no key: every task fakes its progress and a sample rigged
    robot stands in, so the flow can be checked without spending a credit.
    MONSTERS_MOCK=1 forces it even with a key saved; MONSTERS_MOCK_RIGFAIL=1
    fakes a rig failure.
  - every Meshy file it fetches is kept in monsters/.cache/ (gitignored).
    Meshy's links expire after a few days; the cache means a saved monster
    still opens next month. (The hosted page has no such cache.)
"""
import hashlib
import json
import os
import random
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "api"))
from monsters import API, allowed, forward, meshy_asset  # noqa: E402  (api/monsters.py)

CACHE = os.path.join(HERE, ".cache")
PORT = int(os.environ.get("PORT") or os.environ.get("MONSTERS_PORT") or "5320")


def read_key():
    key = os.environ.get("MESHY_API_KEY", "").strip()
    env = os.path.join(HERE, ".env")
    if not key and os.path.exists(env):
        for line in open(env):
            name, _, value = line.partition("=")
            if name.strip() == "MESHY_API_KEY":
                key = value.strip().strip('"').strip("'")
    return key


FORCE_MOCK = bool(os.environ.get("MONSTERS_MOCK"))
KEY = "" if FORCE_MOCK else read_key()
MOCK = not KEY


# ── mock ────────────────────────────────────────────────────────────────────
# A robot from the three.js examples: rigged, with clips named Idle, Wave,
# Dance, Jump, Walking, Running — the same shape of answer Meshy gives.
SAMPLE = "https://threejs.org/examples/models/gltf/RobotExpressive/RobotExpressive.glb"
MOCK_TASKS = {}


def mock_create(kind, body):
    tid = "mock-%s-%06d" % (kind, random.randint(0, 999999))
    MOCK_TASKS[tid] = {"kind": kind, "t0": time.time(), "body": body}
    return {"result": tid}


def mock_get(kind, tid):
    task = MOCK_TASKS.get(tid)
    if not task:
        return 404, {"message": "Not found"}
    span = {"image-to-image": 3, "image-to-3d": 5, "multi-image-to-3d": 5, "rigging": 3, "animations": 2}[kind]
    p = min(100, int((time.time() - task["t0"]) / span * 100))
    out = {"id": tid, "type": kind, "progress": p,
           "status": "SUCCEEDED" if p >= 100 else "IN_PROGRESS"}
    if p < 100:
        return 200, out
    body = task["body"]
    if kind == "image-to-image":
        out["image_urls"] = (body.get("reference_image_urls") or [""])[:1]
    elif kind in ("image-to-3d", "multi-image-to-3d"):
        out["model_urls"] = {"glb": SAMPLE}
    elif kind == "rigging":
        if os.environ.get("MONSTERS_MOCK_RIGFAIL"):
            out["status"] = "FAILED"
            out["task_error"] = {"message": "Rigging failed: the model is not humanoid."}
        else:
            out["result"] = {
                "rigged_character_glb_url": SAMPLE,
                "basic_animations": {"walking_glb_url": SAMPLE, "running_glb_url": SAMPLE},
            }
    elif kind == "animations":
        out["result"] = {"animation_glb_url": SAMPLE}
    return 200, out


# ── server ──────────────────────────────────────────────────────────────────
LOCKS = {}            # one download per cached file, however many clips ask at once
LOCKS_GUARD = threading.Lock()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def log_message(self, fmt, *args):
        if "/api/" in (args[0] if args else ""):
            sys.stderr.write("%s\n" % (fmt % args))

    def end_headers(self):
        # A local tool: never let the browser hold on to a stale page.
        if "p=asset" not in self.path:
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_json(self, code, obj):
        self.send_bytes(code, json.dumps(obj).encode())

    def send_bytes(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if not self.api("GET"):
            super().do_GET()

    def do_POST(self):
        if not self.api("POST"):
            self.send_json(404, {"message": "Not found"})

    def do_DELETE(self):
        if not self.api("DELETE"):
            self.send_json(404, {"message": "Not found"})

    def api(self, method):
        url = urllib.parse.urlparse(self.path)
        if url.path != "/api/monsters":
            return False
        q = urllib.parse.parse_qs(url.query)
        p = q.get("p", [""])[0]
        body = None
        if method == "POST":
            body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        if p == "status":
            self.send_json(200, {"hosted": False, "gated": False, "ready": True, "mock": MOCK})
        elif p == "check":
            self.send_json(200, {"ok": True})
        elif p == "key" and method == "POST":
            self.set_key(json.loads(body or b"{}").get("key", ""))
        elif p == "meshy":
            self.meshy(method, q.get("path", [""])[0], body,
                       "&".join("%s=%s" % (k, urllib.parse.quote(v[0])) for k, v in q.items() if k not in ("p", "path")))
        elif p == "asset":
            self.asset(q.get("url", [""])[0])
        else:
            self.send_json(404, {"message": "Not found"})
        return True

    def set_key(self, key):
        """The page's key box. Checks the key against Meshy's free library call,
        then writes monsters/.env (owner-only) and goes live without a restart."""
        global KEY, MOCK
        if FORCE_MOCK:
            return self.send_json(403, {"message": "This server is mock-only (MONSTERS_MOCK)"})
        key = key.strip()
        if not key.startswith("msy_"):
            return self.send_json(400, {"message": "That doesn't look like a Meshy key — they start with msy_"})
        code, _ = forward("GET", "animations/library", "page_size=1", None, key)
        if code in (401, 403):
            return self.send_json(400, {"message": "Meshy didn't accept that key"})
        if code != 200:
            return self.send_json(502, {"message": "Couldn't check the key with Meshy (%d)" % code})
        fd = os.open(os.path.join(HERE, ".env"), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write("MESHY_API_KEY=%s\n" % key)
        KEY, MOCK = key, False
        return self.send_json(200, {"mock": False})

    def meshy(self, method, path, body, query):
        if not allowed(path):
            return self.send_json(403, {"message": "Not an allowed Meshy path"})
        if MOCK:
            kind, _, tid = path.partition("/")
            if method == "POST":
                return self.send_json(202, mock_create(kind, json.loads(body or b"{}")))
            if method == "DELETE":
                MOCK_TASKS.pop(tid, None)
                return self.send_json(200, {})
            return self.send_json(*mock_get(kind, tid))
        self.send_bytes(*forward(method, path, query, body, KEY))

    def asset(self, src):
        """The whole file in one go (no 4.5MB ceiling here), from the cache when it can."""
        host = urllib.parse.urlparse(src).hostname or ""
        if not (meshy_asset(src) or (MOCK and host == "threejs.org")):
            return self.send_json(403, {"message": "Only Meshy assets are proxied"})
        # Meshy signs its URLs; the path alone names the file.
        name = hashlib.sha1(urllib.parse.urlparse(src).path.encode()).hexdigest()
        ext = os.path.splitext(urllib.parse.urlparse(src).path)[1] or ".bin"
        path = os.path.join(CACHE, name + ext)
        with LOCKS_GUARD:
            lock = LOCKS.setdefault(name, threading.Lock())
        with lock:
            err = None if os.path.exists(path) else self.fetch(src, path)
        if err:
            return self.send_json(502, {"message": "Asset fetch failed: %s" % err})
        types = {".glb": "model/gltf-binary", ".png": "image/png", ".jpg": "image/jpeg",
                 ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp"}
        size = os.path.getsize(path)
        self.send_response(200)
        self.send_header("Content-Type", types.get(ext.lower(), "application/octet-stream"))
        self.send_header("Content-Length", str(size))
        self.send_header("Cache-Control", "max-age=31536000, immutable")
        self.end_headers()
        with open(path, "rb") as f:
            while True:
                chunk = f.read(1 << 16)
                if not chunk:
                    break
                self.wfile.write(chunk)

    def fetch(self, src, path):
        os.makedirs(CACHE, exist_ok=True)
        try:
            with urllib.request.urlopen(src, timeout=120) as r, open(path + ".part", "wb") as f:
                while True:
                    chunk = r.read(1 << 16)
                    if not chunk:
                        break
                    f.write(chunk)
            os.replace(path + ".part", path)
        except Exception as e:
            return e
        return None


if __name__ == "__main__":
    print("Monsters on http://127.0.0.1:%d/monsters/  (%s)" % (PORT, "MOCK — no key" if MOCK else "live Meshy key"))
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
