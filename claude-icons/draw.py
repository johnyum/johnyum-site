"""
Shared drawing language for Anthropic-style icons and illustrations.

Everything in this repo that is drawn in Claude's visual language goes through
these helpers. The point is that the "hand" is reproducible and globally
tunable: wobble lives in the GEOMETRY (jittered anchors, bowed edges), scaled by
one constant W, with only a light noise filter layered on top.

Raising W is what makes the work look childish. Filter-only roughening looks like
a distressed vector rather than a drawn line. Both are the classic failure modes.
"""
import math

# Anthropic's live swatch table, read from anthropic.com CSS variables.
SW = {"slate":"#141413","ivoryL":"#faf9f5","ivoryM":"#f0eee6","ivoryD":"#e8e6dc",
      "clay":"#d97757","accent":"#c6613f","kraft":"#d4a27f","manilla":"#ebdbbc",
      "oat":"#e3dacc","olive":"#788c5d","cactus":"#bcd1ca","fig":"#c46686",
      "heather":"#cbcadb","cloudM":"#b0aea5"}

W = 0.36          # global wobble scale - the difference between drawn and childish


# ----------------------------------------------------------------- primitives
def _n(i, seed, salt):
    h = math.sin((i+1)*12.9898 + seed*78.233 + salt*39.346) * 43758.5453
    return (h - math.floor(h)) - 0.5


def jit(pts, seed, amt):
    a = amt * W
    return [(x + _n(i,seed,1)*2*a, y + _n(i,seed,2)*2*a) for i,(x,y) in enumerate(pts)]


def curve(pts, seed=0, closed=True, amt=3.0, t=1.0):
    """Smooth Catmull-Rom through jittered anchors. For organic contours."""
    p = jit(pts, seed, amt); n = len(p)
    P = (lambda i: p[i % n]) if closed else (lambda i: p[max(0, min(n-1, i))])
    d = "M%.1f,%.1f" % P(0)
    for i in (range(n) if closed else range(n-1)):
        a, b, c, e = P(i-1), P(i), P(i+1), P(i+2)
        d += " C%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
            b[0]+(c[0]-a[0])/6*t, b[1]+(c[1]-a[1])/6*t,
            c[0]-(e[0]-b[0])/6*t, c[1]-(e[1]-b[1])/6*t, c[0], c[1])
    return d + (" Z" if closed else "")


def poly(pts, seed=0, closed=True, amt=2.4, bow=2.2):
    """Sharp corners, gently bowed edges. For hand-ruled straight lines."""
    p = jit(pts, seed, amt); n = len(p)
    seq = list(range(n)) if closed else list(range(n-1))
    d = "M%.1f,%.1f" % p[0]
    for k, i in enumerate(seq):
        a, b = p[i], p[(i+1) % n]
        dx, dy = b[0]-a[0], b[1]-a[1]; L = math.hypot(dx, dy) or 1
        off = _n(k, seed, 3) * 2 * bow * W
        d += " Q%.1f,%.1f %.1f,%.1f" % (
            (a[0]+b[0])/2 - dy/L*off, (a[1]+b[1])/2 + dx/L*off, b[0], b[1])
    return d + (" Z" if closed else "")


def circ(cx, cy, r, seed=0, amt=2.2, k=16):
    return curve([(cx + r*math.cos(i*2*math.pi/k), cy + r*math.sin(i*2*math.pi/k))
                  for i in range(k)], seed, True, amt)


def scribble(cx, cy, r=46, steps=420, seed=0):
    """Overlapping wandering loops - a knot, not a rosette."""
    pts = []
    for i in range(steps+1):
        t = i/steps * 2*math.pi * 7
        pts.append((cx + r*math.cos(t) + .62*r*math.cos(2.37*t+.7) + .30*r*math.sin(3.9*t),
                    cy + r*math.sin(t)*.92 + .58*r*math.sin(2.11*t+1.9) + .26*r*math.cos(4.3*t)))
    return "M%.1f,%.1f " % pts[0] + " ".join("L%.1f,%.1f" % q for q in pts[1:])


# ----------------------------------------------------------------- emit
def I(d, c="ink"):  return '<path class="%s" d="%s"/>' % (c, d)
def A(d):           return '<path class="acc" d="%s"/>' % d
def S(d):           return '<path class="solid" d="%s"/>' % d
# Paper: an opaque sheet in the ground colour, so overlapping shapes can
# occlude each other. Everything here is stroke-only otherwise, which means
# a back shape's interior detail reads straight through whatever is in front.
def P(d):           return '<path class="paper" d="%s"/>' % d


TPL = """<svg viewBox="0 0 {g} {g}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label}">
<defs><filter id="p-{n}" x="-16%" y="-16%" width="132%" height="132%">
<feTurbulence type="fractalNoise" baseFrequency="{bf}" numOctaves="2" seed="{s}" result="w"/>
<feDisplacementMap in="SourceGraphic" in2="w" scale="{ds}" xChannelSelector="R" yChannelSelector="G" result="m"/>
<feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="2" seed="{s2}" result="g"/>
<feDisplacementMap in="m" in2="g" scale="0.9" xChannelSelector="R" yChannelSelector="G"/>
</filter>
<filter id="q-{n}" x="-18%" y="-18%" width="136%" height="136%">
<feTurbulence type="fractalNoise" baseFrequency="{bf2}" numOctaves="2" seed="{s2}" result="w"/>
<feDisplacementMap in="SourceGraphic" in2="w" scale="{ds2}" xChannelSelector="R" yChannelSelector="G"/>
</filter></defs>
<style>
.ink{{fill:none;stroke:{slate};stroke-width:{sw};stroke-linecap:round;stroke-linejoin:round}}
.ink-thin{{fill:none;stroke:{slate};stroke-width:{swt};stroke-linecap:round;stroke-linejoin:round}}
.solid{{fill:{slate}}}
.paper{{fill:{paper}}}
.acc{{fill:var(--acc,{acc})}}
.acc-line{{fill:none;stroke:var(--acc,{acc});stroke-width:{swt};stroke-linecap:round;stroke-linejoin:round}}
</style>
<g filter="url(#q-{n})" opacity=".95">{accent}</g>
<g filter="url(#p-{n})">{ink}</g>
</svg>
"""


def render(name, label, ink, accent="", acc="#d97757", seed=0, grid=256, sw=11, swt=8.5):
    """Build one self-contained SVG. grid=256 for icons, 512 for illustrations."""
    k = grid / 256.0
    return TPL.format(
        n=name, label=label, g=grid, s=seed*7+3, s2=seed*13+11,
        slate=SW["slate"], paper=SW["ivoryL"], acc=acc, accent=accent, ink=ink,
        sw=round(sw, 2), swt=round(swt, 2),
        bf="%.4f %.4f" % (0.024/k, 0.031/k), ds=round(2.8*k, 2),
        bf2="%.4f %.4f" % (0.018/k, 0.026/k), ds2=round(5*k, 2))
