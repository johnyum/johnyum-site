"""Roma's first solids — six foods a seven-month-old can eat.

Drawn as ICONS rather than illustrations on purpose: they sit inside small
circular wells in the app's baby widget, and the icon tier is the one built
to survive at that size. Each one is a silhouette a stranger could name with
its colour plate removed.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from draw import SW, jit, curve, poly, circ, scribble, I, A, S, render

OFF = lambda pts, dx=-8, dy=8: [(x + dx, y + dy) for x, y in pts]


def _arc(cx, cy, r, a0, a1, n=9):
    """Points along an arc, degrees, y down."""
    return [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
            for a in [a0 + (a1 - a0) * i / (n - 1) for i in range(n)]]


def _crescent(cx, cy, R, thick, a0, a1, n=11):
    """A crescent whose two arcs MEET at the tips, so the ends come to a
    point. Offsetting the arcs instead leaves blunt ends, and a blunt
    crescent reads as a bowl."""
    out, inn = [], []
    for i in range(n):
        t = i / (n - 1)
        a = math.radians(a0 + (a1 - a0) * t)
        # Skewed so the belly sits off centre; a symmetric
        # crescent reads as a smile rather than a fruit.
        r = R - thick * math.sin(math.pi * t ** 0.78)
        out.append((cx + R * math.cos(a), cy + R * math.sin(a)))
        inn.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out + list(reversed(inn))


def _rot(pts, deg, cx=128, cy=128):
    a = math.radians(deg)
    return [(cx + (x - cx) * math.cos(a) - (y - cy) * math.sin(a),
             cy + (x - cx) * math.sin(a) + (y - cy) * math.cos(a)) for x, y in pts]


def _tuber(x0, x1, y, thick, bend, n=11):
    """A long body that tapers to a point at both ends. Without the taper
    every root vegetable settles into the same oval and reads as a roll."""
    top, bot = [], []
    for i in range(n):
        t = i / (n - 1)
        x = x0 + (x1 - x0) * t
        cy = y + bend * math.sin(math.pi * t)
        h = thick * math.sin(math.pi * t) ** 0.62
        top.append((x, cy - h))
        bot.append((x, cy + h))
    return top + list(reversed(bot))


def avocado():
    """Halved: the stone is what separates it from a pear."""
    body = [(128, 26), (162, 44), (182, 78), (186, 122), (172, 168),
            (146, 206), (128, 216), (110, 206), (84, 168), (70, 122),
            (74, 78), (94, 44)]
    return (I(curve(body, 4000, amt=2.2))
          + I(circ(128, 152, 38, 4001), "ink-thin")), \
           A(curve(OFF(body), 4002, amt=4))


def banana():
    """A thick crescent, belly off centre and the whole thing tilted — held
    level and symmetric it reads as a smile."""
    body = _rot(_crescent(128, 54, 116, 62, 18, 162), -22)
    return I(curve(body, 4010, amt=2.0, t=.8)), \
           A(curve(OFF(body), 4012, amt=4))


def pear():
    """A narrow neck circle over a wide body circle, outlined by taking the
    wider of the two at every height. That is what puts a real shoulder in
    it. Placing anchors by hand pinched a waist; growing a radius linearly
    made a cone; the piriform curve closed to a point at both ends."""
    y1, r1, y2, r2 = 96.0, 34.0, 168.0, 66.0
    top, bot = y1 - r1, y2 + r2
    right = []
    for i in range(20):
        # Cosine spacing: more samples at the ends, where the curvature is.
        t = (1 - math.cos(math.pi * i / 19)) / 2
        y = top + (bot - top) * t
        w = 0.0
        for cy, r in ((y1, r1), (y2, r2)):
            if abs(y - cy) < r:
                w = max(w, math.sqrt(r * r - (y - cy) ** 2))
        right.append((128 + w, y))
    body = right + [(256 - x, y) for x, y in reversed(right)]
    return (I(curve(body, 4030, amt=1.8, t=.9))
          + I(curve([(128, 64), (138, 34)], 4031, False))), \
           A(curve(OFF(body), 4033, amt=4))


def carrot():
    """Root down to a point, three fronds up. Two rings for the grain."""
    root = [(128, 236), (94, 132), (162, 132)]
    fronds = "".join(I(curve(p, 4041 + i, False)) for i, p in enumerate([
        [(120, 132), (96, 96), (86, 62)],
        [(128, 130), (128, 90), (126, 52)],
        [(136, 132), (162, 98), (174, 66)]]))
    return (I(poly(root, 4040, bow=2.0))
          + fronds
          + I(curve([(108, 168), (146, 168)], 4044, False), "ink-thin")
          + I(curve([(116, 196), (140, 196)], 4045, False), "ink-thin")), \
           A(poly(OFF(root), 4046, bow=3))


def peas():
    """A pod, pointed at both ends, with three peas showing."""
    pod = [(28, 146), (68, 108), (126, 94), (184, 106), (228, 146),
           (184, 184), (126, 198), (68, 186)]
    return (I(curve(pod, 4050, amt=2.4, t=.8))
          + I(circ(84, 146, 21, 4051), "ink-thin")
          + I(circ(128, 148, 23, 4052), "ink-thin")
          + I(circ(172, 146, 21, 4053), "ink-thin")), \
           A(curve(OFF(pod), 4054, amt=4))


ICONS = [("avocado", "Avocado", "olive", avocado),
         ("banana", "Banana", "manilla", banana),
         ("pear", "Pear", "cactus", pear),
         ("carrot", "Carrot", "clay", carrot),
         ("peas", "Peas", "olive", peas)]
