#!/usr/bin/env python3
"""Measure a device-chrome PNG's screen cut-out and print the CSS vars for it.

The chrome is a photographed phone whose screen is a TRANSPARENT hole — but so
is everything OUTSIDE the phone body, so a plain alpha bounding box just returns
the whole image. Instead this flood-fills the transparent region that contains
the image centre: that component is the screen and nothing else.

Prints the numbers slides/11.html's --frame-*/--s* vars want, all as percentages
of the frame's own box. Re-run it if the chrome asset is ever swapped.

    python3 tools/measure-frame.py slides/assets/device/iphone-frame.png
"""
import sys
from collections import deque

from PIL import Image

path = sys.argv[1] if len(sys.argv) > 1 else "slides/assets/device/iphone-frame.png"
im = Image.open(path).convert("RGBA")
W, H = im.size
alpha = im.getchannel("A").load()

CLEAR = 8  # alpha at or below this counts as a hole


def clear(x, y):
    return alpha[x, y] <= CLEAR


start = (W // 2, H // 2)
if not clear(*start):
    sys.exit("the centre of %s is opaque — is the screen actually cut out?" % path)

# flood fill the screen hole (4-connected; the island/notch is opaque and simply
# sits inside the component without splitting it)
seen = bytearray(W * H)
q = deque([start])
seen[start[1] * W + start[0]] = 1
x0 = x1 = start[0]
y0 = y1 = start[1]
while q:
    x, y = q.popleft()
    if x < x0: x0 = x
    if x > x1: x1 = x
    if y < y0: y0 = y
    if y > y1: y1 = y
    for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
        if 0 <= nx < W and 0 <= ny < H and not seen[ny * W + nx] and clear(nx, ny):
            seen[ny * W + nx] = 1
            q.append((nx, ny))

w, h = x1 - x0 + 1, y1 - y0 + 1

# corner radius: how far down from the top of the hole before its left edge
# reaches the full width — that run is the arc
radius = 0
for y in range(y0, y0 + h):
    row = next((x for x in range(x0, x1 + 1) if seen[y * W + x]), None)
    if row is not None and row <= x0:
        radius = y - y0
        break

print(f"frame      {W} x {H}")
print(f"screen     x {x0}..{x1}  y {y0}..{y1}   ({w} x {h})")
print(f"radius     ~{radius}px")
print()
print("  --frame-w: %d;" % W)
print("  --frame-h: %d;" % H)
print("  --sx: %.3f%%;" % (100 * x0 / W))
print("  --sy: %.3f%%;" % (100 * y0 / H))
print("  --sw: %.3f%%;" % (100 * w / W))
print("  --sh: %.3f%%;" % (100 * h / H))
print("  --sr: %.3f%%;" % (100 * radius / w))
print("  --sry: %.3f%%;" % (100 * radius / h))
print()
print("screen aspect %.4f  (the Figma screen is 375x811 = 0.4624)" % (w / h))
