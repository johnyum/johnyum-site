"""johnyum.com/monsters — the hosted half of the sketch-to-monster pipeline.

A Vercel Python function: stdlib only, no requirements.txt. It holds the Meshy
key so the page never sees it, and lets nobody spend credits without the
passcode. Locally, monsters/serve.py imports the same helpers from this file.

Vercel env vars (Project → Settings → Environment Variables):
  MESHY_API_KEY        msy_...                     required
  MONSTERS_PASSCODE    whatever you'll type in     required — no passcode, no building
  MONSTERS_DAILY_CAP   builds per 24 hours         optional — unset means no limit

One route, /api/monsters?p=...  (a file in /api wins over vercel.json's /api/* → Trips rewrite):
  status                         {"hosted": true, "gated": true, "ready": bool}
  check   POST                   200 if the X-Monsters-Pass header is right, else 401
  meshy   &path=<kind>[/<id>]    proxied to https://api.meshy.ai/openapi/v1/<path>
  asset   &url=…&start=&end=     one ≤4MB slice of a Meshy file. Meshy's files send no
                                 CORS header, and a Vercel response stops at 4.5MB, so
                                 the page pulls a model through here a slice at a time.

The cap is counted from Meshy's own task list, not stored here: it covers every
build on the account, including ones made locally.
"""
import hmac
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler

API = "https://api.meshy.ai/openapi/v1/"
ALLOWED = ("image-to-image", "image-to-3d", "multi-image-to-3d", "rigging", "animations")
CHUNK = 4 * 1024 * 1024
# Only the two steps that start a build are capped; rig and moves follow from them.
CAPPED = ("image-to-image", "image-to-3d", "multi-image-to-3d")


def allowed(path):
    return path.split("/")[0] in ALLOWED and ".." not in path and "//" not in path


def forward(method, path, query, body, key):
    """One call to Meshy. Returns (status, bytes); never raises."""
    req = urllib.request.Request(
        API + path + ("?" + query if query else ""), data=body, method=method,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=50) as r:
            return r.status, r.read() or b"{}"
    except urllib.error.HTTPError as e:
        return e.code, e.read() or b"{}"
    except Exception as e:  # network down, DNS, timeout
        return 502, json.dumps({"message": str(e)}).encode()


def over_cap(kind, key, cap):
    """True when `kind` has been started `cap` times in the last 24 hours."""
    code, data = forward("GET", kind, "page_size=100&sort_by=-created_at", None, key)
    if code != 200:
        return False  # can't count — let Meshy's own limits decide
    since = (time.time() - 86400) * 1000
    tasks = json.loads(data)
    return sum(1 for t in tasks if (t.get("created_at") or 0) >= since) >= cap


def meshy_asset(src):
    host = urllib.parse.urlparse(src).hostname or ""
    return src.startswith("https://") and (host == "meshy.ai" or host.endswith(".meshy.ai"))


# ── the face: where a creature's eyes, mouth and nose are, so its fur stays off them ──
# Fuzzball renders the bare model straight on and asks Claude to box each feature; the page
# then shaves those spots. Stdlib HTTP like the rest of this file (no requirements.txt here).
FACE_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["features"],
    "properties": {"features": {"type": "array", "items": {
        "type": "object", "additionalProperties": False, "required": ["view", "kind", "x", "y", "w", "h"],
        "properties": {
            "view": {"type": "string", "enum": ["A", "B"]},
            "kind": {"type": "string", "enum": ["eye", "mouth", "nose", "brow"]},
            "x": {"type": "number"}, "y": {"type": "number"}, "w": {"type": "number"}, "h": {"type": "number"},
        }}}},
}
FACE_PROMPT = (
    "Images A and B are straight-on renders of one 3D cartoon character on white, from opposite sides (one is "
    "its front, one its back). Fur is about to be grown over its whole surface, and its face must stay clear. "
    "On the image that shows its face, box every eye (the whole eye, whites included), the mouth, the nose and "
    "any eyebrows that are painted or sculpted on it, and say which image (view A or B). Boxes are fractions of "
    "that image: x and y are the top-left corner, w and h the size, all from 0 to 1, drawn tightly round each "
    "feature. If it has no face on either side, return no features.")


def anthropic_key():
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "monsters", ".env")
    if not key and os.path.exists(env):
        for line in open(env):
            name, _, value = line.partition("=")
            if name.strip() == "ANTHROPIC_API_KEY":
                key = value.strip().strip('"').strip("'")
    return key


def find_face(images):
    """images: [front, back] as data:image/png;base64,… URLs. Returns (status, {"features": [...]})."""
    key = anthropic_key()
    if not key:
        return 503, {"message": "No ANTHROPIC_API_KEY — the face can't be found automatically"}
    content = []
    for label, image in zip("AB", (images or [])[:2]):
        head, _, data = (image or "").partition(",")
        media = head[5:].split(";")[0] if head.startswith("data:") else ""
        if media not in ("image/png", "image/jpeg") or not data or len(data) > 6_000_000:
            return 400, {"message": "Send PNG or JPEG data URLs"}
        content += [{"type": "text", "text": "Image %s:" % label},
                    {"type": "image", "source": {"type": "base64", "media_type": media, "data": data}}]
    if not content:
        return 400, {"message": "Send the two renders"}
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", method="POST", data=json.dumps({
        "model": "claude-opus-5-5", "max_tokens": 16000,
        "output_config": {"effort": "low", "format": {"type": "json_schema", "schema": FACE_SCHEMA}},
        "fallbacks": "default",
        "messages": [{"role": "user", "content": content + [{"type": "text", "text": FACE_PROMPT}]}],
    }).encode(), headers={"x-api-key": key, "anthropic-version": "2026-10-21",
                          "anthropic-beta": "server-side-fallback-2026-07-01", "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=55) as r:
            msg = json.loads(r.read())
    except urllib.error.HTTPError as e:
        return 502, {"message": "Claude said %d: %s" % (e.code, e.read()[:200].decode("utf-8", "replace"))}
    except Exception as e:
        return 502, {"message": str(e)}
    if msg.get("stop_reason") == "refusal":
        return 200, {"features": []}
    text = "".join(b.get("text", "") for b in msg.get("content", []) if b.get("type") == "text")
    try:
        out = json.loads(text)
    except ValueError:
        return 502, {"message": "Couldn't read Claude's answer"}
    clamp = lambda v: max(0.0, min(1.0, float(v)))
    return 200, {"features": [{"view": f["view"], "kind": f["kind"], "x": clamp(f["x"]), "y": clamp(f["y"]),
                               "w": clamp(f["w"]), "h": clamp(f["h"])} for f in out.get("features", [])][:12]}


class handler(BaseHTTPRequestHandler):
    def send_json(self, code, obj):
        self.send_bytes(code, json.dumps(obj).encode())

    def send_bytes(self, code, data, ctype="application/json", extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def q(self):
        return urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

    def authed(self):
        want = os.environ.get("MONSTERS_PASSCODE", "")
        got = self.headers.get("X-Monsters-Pass", "")
        return bool(want) and hmac.compare_digest(want.encode(), got.encode())

    def do_GET(self):
        self.route("GET")

    def do_POST(self):
        self.route("POST")

    def do_DELETE(self):
        self.route("DELETE")

    def route(self, method):
        q = self.q()
        p = q.get("p", [""])[0]
        key = os.environ.get("MESHY_API_KEY", "")
        if p == "status":
            return self.send_json(200, {"hosted": True, "gated": True,
                                        "ready": bool(key and os.environ.get("MONSTERS_PASSCODE"))})
        if not self.authed():
            return self.send_json(401, {"message": "Wrong passcode"})
        if p == "check":
            return self.send_json(200, {"ok": True})

        if p == "face" and method == "POST":
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
            return self.send_json(*find_face(body.get("images") or []))

        if not key:
            return self.send_json(503, {"message": "Building is switched off — no Meshy key on the server"})

        if p == "meshy":
            path = q.get("path", [""])[0]
            if not allowed(path):
                return self.send_json(403, {"message": "Not an allowed Meshy path"})
            body = None
            if method == "POST":
                body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
                kind = path.split("/")[0]
                cap = int(os.environ.get("MONSTERS_DAILY_CAP") or 0)   # 0: no limit (John's call, 2026-10-03)
                if cap and "/" not in path and kind in CAPPED and over_cap(kind, key, cap):
                    return self.send_json(429, {"message": "That's today's limit of %d monsters — try again tomorrow" % cap})
            query = "&".join("%s=%s" % (k, urllib.parse.quote(v[0])) for k, v in q.items() if k not in ("p", "path"))
            code, data = forward(method, path, query, body, key)
            if code in (401, 403):
                # Meshy refusing the server's key is not a wrong passcode — the page
                # reads a 401 as "ask for the passcode again", so it mustn't see one.
                return self.send_json(502, {"message": "Meshy turned down the server's key"})
            return self.send_bytes(code, data)

        if p == "asset":
            src = q.get("url", [""])[0]
            if not meshy_asset(src):
                return self.send_json(403, {"message": "Only Meshy assets"})
            start = int(q.get("start", ["0"])[0])
            end = min(int(q.get("end", [str(CHUNK - 1)])[0]), start + CHUNK - 1)
            req = urllib.request.Request(src, headers={"Range": "bytes=%d-%d" % (start, end)})
            try:
                with urllib.request.urlopen(req, timeout=50) as r:
                    data = r.read()
                    rng = r.headers.get("Content-Range") or ""
            except Exception as e:
                return self.send_json(502, {"message": "Asset fetch failed: %s" % e})
            total = rng.rsplit("/", 1)[-1] if "/" in rng else str(len(data))
            return self.send_bytes(200, data, "application/octet-stream",
                                   {"X-Total-Size": total, "Access-Control-Expose-Headers": "X-Total-Size"})

        return self.send_json(404, {"message": "Not found"})
