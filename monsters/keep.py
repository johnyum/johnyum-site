#!/usr/bin/env python3
"""Keep a finished monster for good: one small GLB in peek/monsters/, in the repo.

Meshy's file links are signed and its files are deleted after 3 days, so a Peek
link built from them dies with them. This merges what a build made into one file
that ships with the site:

  - the rigged model (or the bare model, for one that couldn't take a skeleton)
  - every move's animation, copied onto it by bone name and named by its label
    (Idle, Wave, Dance, Jump, Walk, Run) — Meshy hands each move back as the whole
    32MB model again, so only the animation data is taken from each
  - the textures shrunk to 1024 (sips), which is plenty at chat size

Stdlib only, as the rest of Monsters is. serve.py calls keep() when a build
finishes; from the shell it rescues a build made on johnyum.com while Meshy
still has it (within 3 days):

    python3 monsters/keep.py <rig task id> [name]
"""
import json
import os
import re
import struct
import subprocess
import sys
import tempfile
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "peek", "monsters")
TEXTURE = 1024


# ── GLB in and out ──────────────────────────────────────────────────────────

def read_glb(data):
    """(json, [bytes of each bufferView])."""
    magic, _, _ = struct.unpack_from("<III", data, 0)
    if magic != 0x46546C67:
        raise ValueError("not a GLB")
    at, doc, binary = 12, None, b""
    while at < len(data):
        n, kind = struct.unpack_from("<II", data, at)
        chunk = data[at + 8: at + 8 + n]
        if kind == 0x4E4F534A:
            doc = json.loads(chunk)
        elif kind == 0x004E4942:
            binary = chunk
        at += 8 + n
    views = [binary[v.get("byteOffset", 0): v.get("byteOffset", 0) + v["byteLength"]]
             for v in doc.get("bufferViews", [])]
    return doc, views


def write_glb(doc, views):
    """Lay the views out again, 4-byte aligned, in one buffer."""
    out = bytearray()
    for v, data in zip(doc["bufferViews"], views):
        out += b"\0" * (-len(out) % 4)
        v["buffer"], v["byteOffset"], v["byteLength"] = 0, len(out), len(data)
        out += data
    out += b"\0" * (-len(out) % 4)
    doc["buffers"] = [{"byteLength": len(out)}]
    js = json.dumps(doc, separators=(",", ":")).encode()
    js += b" " * (-len(js) % 4)
    total = 12 + 8 + len(js) + 8 + len(out)
    return (struct.pack("<III", 0x46546C67, 2, total) + struct.pack("<II", len(js), 0x4E4F534A) + js
            + struct.pack("<II", len(out), 0x004E4942) + bytes(out))


# ── the parts ───────────────────────────────────────────────────────────────

def shrink_images(doc, views, size=TEXTURE):
    """Each embedded texture down to `size` on its long side, same format."""
    for img in doc.get("images", []):
        if "bufferView" not in img:
            continue
        mime = img.get("mimeType", "image/png")
        ext = ".jpg" if "jpeg" in mime else ".png"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "t" + ext)
            with open(path, "wb") as f:
                f.write(views[img["bufferView"]])
            args = ["sips", "-Z", str(size)]
            if ext == ".jpg":
                args += ["-s", "formatOptions", "85"]
            r = subprocess.run(args + [path], capture_output=True)
            if r.returncode == 0:
                with open(path, "rb") as f:
                    small = f.read()
                if len(small) < len(views[img["bufferView"]]):
                    views[img["bufferView"]] = small


def add_animation(doc, views, clip_doc, clip_views, label):
    """Copy the clip file's longest animation onto this model, by node name."""
    anims = clip_doc.get("animations") or []
    if not anims:
        return False
    names = {n.get("name"): i for i, n in enumerate(doc["nodes"]) if n.get("name")}

    def length(a):
        return max((clip_doc["accessors"][s["input"]].get("max", [0])[0] for s in a["samplers"]), default=0)

    src = max(anims, key=length)
    copied = {}

    def accessor(i):
        if i not in copied:
            a = dict(clip_doc["accessors"][i])
            v = dict(clip_doc["bufferViews"][a["bufferView"]])
            v.pop("byteOffset", None)
            doc["bufferViews"].append(v)
            views.append(clip_views[a["bufferView"]])
            a["bufferView"] = len(doc["bufferViews"]) - 1
            doc.setdefault("accessors", []).append(a)
            copied[i] = len(doc["accessors"]) - 1
        return copied[i]

    samplers, channels = [], []
    for ch in src["channels"]:
        node = clip_doc["nodes"][ch["target"]["node"]].get("name")
        if node not in names:
            continue
        s = src["samplers"][ch["sampler"]]
        samplers.append({"input": accessor(s["input"]), "output": accessor(s["output"]),
                         "interpolation": s.get("interpolation", "LINEAR")})
        channels.append({"sampler": len(samplers) - 1,
                         "target": {"node": names[node], "path": ch["target"]["path"]}})
    if not channels:
        return False
    doc.setdefault("animations", []).append({"name": label, "samplers": samplers, "channels": channels})
    return True


def slim_mesh(doc, views):
    """Tangents out (three.js derives its own from the normal map), skin weights
    from 32-bit floats to 16-bit — together about a quarter of a Meshy model."""
    for mesh in doc.get("meshes", []):
        for prim in mesh.get("primitives", []):
            attrs = prim.get("attributes", {})
            attrs.pop("TANGENT", None)
            w = attrs.get("WEIGHTS_0")
            if w is None:
                continue
            a = doc["accessors"][w]
            v = doc["bufferViews"][a.get("bufferView", -1)] if "bufferView" in a else None
            if a.get("componentType") != 5126 or a.get("byteOffset", 0) or not v or v.get("byteStride"):
                continue
            n = a["count"]
            floats = struct.unpack_from("<%df" % (n * 4), views[a["bufferView"]], 0)
            out = []
            for i in range(0, n * 4, 4):
                w = [max(0.0, x) for x in floats[i:i + 4]]
                total = sum(w)
                q = [min(65535, round(x / total * 65535)) for x in w] if total else [0, 0, 0, 0]
                if total:
                    q[q.index(max(q))] += 65535 - sum(q)   # each vertex's weights sum to exactly one
                out += q
            doc["bufferViews"].append({"byteLength": n * 8})
            views.append(struct.pack("<%dH" % (n * 4), *out))
            doc["accessors"].append({"bufferView": len(views) - 1, "componentType": 5123,
                                     "normalized": True, "count": n, "type": "VEC4"})
            attrs["WEIGHTS_0"] = len(doc["accessors"]) - 1


def prune(doc, views):
    """Drop every accessor and bufferView nothing points at any more, and renumber."""
    used_acc = set()
    for mesh in doc.get("meshes", []):
        for prim in mesh.get("primitives", []):
            used_acc.update(prim.get("attributes", {}).values())
            if "indices" in prim:
                used_acc.add(prim["indices"])
            for t in prim.get("targets", []):
                used_acc.update(t.values())
    for skin in doc.get("skins", []):
        if "inverseBindMatrices" in skin:
            used_acc.add(skin["inverseBindMatrices"])
    for anim in doc.get("animations", []):
        for s in anim["samplers"]:
            used_acc.update((s["input"], s["output"]))
    acc_map = {old: new for new, old in enumerate(sorted(used_acc))}
    accessors = [doc["accessors"][i] for i in sorted(used_acc)]
    used_view = {a["bufferView"] for a in accessors if "bufferView" in a}
    used_view |= {img["bufferView"] for img in doc.get("images", []) if "bufferView" in img}
    view_map = {old: new for new, old in enumerate(sorted(used_view))}
    for a in accessors:
        if "bufferView" in a:
            a["bufferView"] = view_map[a["bufferView"]]
    for img in doc.get("images", []):
        if "bufferView" in img:
            img["bufferView"] = view_map[img["bufferView"]]
    for mesh in doc.get("meshes", []):
        for prim in mesh.get("primitives", []):
            prim["attributes"] = {k: acc_map[v] for k, v in prim.get("attributes", {}).items()}
            if "indices" in prim:
                prim["indices"] = acc_map[prim["indices"]]
            prim["targets"] = [{k: acc_map[v] for k, v in t.items()} for t in prim.get("targets", [])]
            if not prim["targets"]:
                del prim["targets"]
    for skin in doc.get("skins", []):
        if "inverseBindMatrices" in skin:
            skin["inverseBindMatrices"] = acc_map[skin["inverseBindMatrices"]]
    for anim in doc.get("animations", []):
        for s in anim["samplers"]:
            s["input"], s["output"] = acc_map[s["input"]], acc_map[s["output"]]
    doc["accessors"] = accessors
    doc["bufferViews"] = [doc["bufferViews"][i] for i in sorted(used_view)]
    views[:] = [views[i] for i in sorted(used_view)]


def merge(model, clips):
    """model: GLB bytes. clips: {label: GLB bytes}. Returns (GLB bytes, labels kept)."""
    doc, views = read_glb(model)
    doc.pop("extras", None)
    kept = []
    for label, data in clips.items():
        try:
            cdoc, cviews = read_glb(data)
            if add_animation(doc, views, cdoc, cviews, label):
                kept.append(label)
        except Exception as e:  # one bad move never loses the others
            sys.stderr.write("keep: skipped %s (%s)\n" % (label, e))
    shrink_images(doc, views)
    slim_mesh(doc, views)
    prune(doc, views)
    return write_glb(doc, views), kept


def slug(name):
    s = re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")[:40]
    return s or "monster"


def keep(model_url, clips, name, fetch):
    """Merge, write peek/monsters/<name>.glb, return its site path and what it holds.
    fetch(url) -> bytes; serve.py hands over its cache, the shell plain urllib."""
    out, kept = merge(fetch(model_url), {k: fetch(u) for k, u in (clips or {}).items() if u})
    os.makedirs(OUT, exist_ok=True)
    fname = slug(name) + ".glb"
    with open(os.path.join(OUT, fname), "wb") as f:
        f.write(out)
    return {"file": "/peek/monsters/" + fname, "clips": kept, "bytes": len(out)}


# ── from the shell: rescue a build Meshy still has ──────────────────────────

CLIP_NAMES = (("Idle", "idle"), ("Wave", "wav"), ("Wave", "hello"), ("Dance", "danc"), ("Jump", "jump"))


def label_of(glb):
    """A move file's label, from the animation name Meshy gave it."""
    doc, _ = read_glb(glb)
    name = " ".join(a.get("name", "") for a in doc.get("animations", [])).lower()
    for label, key in CLIP_NAMES:
        if key in name:
            return label
    m = re.search(r"\|([^|]+)\|", name)
    return (m.group(1) if m else "Move").title()


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.path.insert(0, os.path.join(ROOT, "api"))
    from monsters import forward  # api/monsters.py
    sys.path.insert(0, HERE)
    from serve import read_key
    key = read_key()
    if not key:
        sys.exit("No Meshy key — put MESHY_API_KEY in monsters/.env")
    rig_id, name = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else sys.argv[1][:8])
    code, data = forward("GET", "rigging/" + rig_id, "", None, key)
    if code != 200:
        sys.exit("Meshy: %s" % data.decode()[:200])
    rig = json.loads(data)
    res = rig["result"]
    fetch = lambda u: urllib.request.urlopen(u, timeout=120).read()  # noqa: E731
    # The moves aren't tagged with their rig, so take the ones started just after it.
    code, data = forward("GET", "animations", "page_size=50&sort_by=-created_at", None, key)
    done = rig.get("finished_at") or rig["created_at"]
    moves = [t for t in json.loads(data) if t["status"] == "SUCCEEDED" and done <= t["created_at"] <= done + 5 * 60 * 1000]
    clips = {}
    for t in moves:
        g = fetch(t["result"]["animation_glb_url"])
        clips[label_of(g)] = g
    for label, k in (("Walk", "walking_glb_url"), ("Run", "running_glb_url")):
        if res.get("basic_animations", {}).get(k):
            clips[label] = fetch(res["basic_animations"][k])
    print("rig %s, %d moves: %s" % (rig_id[:8], len(clips), ", ".join(clips)))
    t0 = time.time()
    out, kept = merge(fetch(res["rigged_character_glb_url"]), clips)
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, slug(name) + ".glb")
    with open(path, "wb") as f:
        f.write(out)
    print("kept %s — %.1f MB, %s (%.1fs)" % (os.path.relpath(path, ROOT), len(out) / 1e6, ", ".join(kept), time.time() - t0))
    print("Peek: /peek/#m=%s" % pack({"file": "/peek/monsters/" + slug(name) + ".glb"}))


def pack(obj):
    """kit.js's pack(): base64url of the JSON, no padding."""
    import base64
    return base64.urlsafe_b64encode(json.dumps(obj, separators=(",", ":")).encode()).decode().rstrip("=")


if __name__ == "__main__":
    main()
