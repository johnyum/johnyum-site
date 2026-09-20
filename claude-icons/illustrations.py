"""
Editorial illustrations in Claude's visual language.

Same hand as the icons (see draw.py) but a thinner relative line and a larger,
narrative composition - the tier used for blog cards, empty states, headers and
spot art. Anthropic's motif vocabulary is humanistic: hands above all, then
profiles, bulbs, books, botanicals, knots and node constellations. Reach for a
hand before you reach for a gear.

    python3 claude-icons/illustrations.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw import SW, curve, poly, circ, scribble, I, A, S, P, render

OUT = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(OUT, "illustrations")
os.makedirs(DIR, exist_ok=True)

mx = lambda pts: [(256-x, y) for x, y in pts]          # mirror across the centre

# --------------------------------------------------------------- the pieces
def hand():
    """The signature motif. Comb fingers, closed palm loop."""
    p = [(88,208),(83,168),(88,126),
         (93,74),(100,66),(107,74),(108,112),
         (113,60),(120,52),(127,60),(128,114),
         (133,62),(140,54),(147,62),(148,118),
         (153,78),(160,70),(166,78),(168,132),
         (172,160),(172,186),(160,204),(134,214),(108,214),(92,212)]
    return I(curve(p,1,amt=2.0,t=.55)), A(circ(168,84,62,9,amt=5))

def care():
    """Two hands cupped around something rising."""
    L = [(40,212),(38,178),(48,142),(62,122),
         (66,84),(74,78),(79,90),(72,122),
         (85,76),(93,72),(97,84),(89,124),
         (103,82),(111,80),(114,92),(105,128)]
    form = [(128,34),(158,64),(176,104),(182,146),(74,146),(80,104),(98,64)]
    return (I(curve(L,2,False,amt=2.0,t=.6)) + I(curve(mx(L),3,False,amt=2.0,t=.6))), \
           A(curve([(x-9,y+9) for x,y in form],10,amt=4))

def reasoning():
    """Profile with a node constellation - thinking made visible."""
    head = [(94,56),(126,44),(158,54),(176,80),(178,108),(168,140),(154,164),
            (154,190),(156,214),(74,214),(74,190),(70,174),(54,152),(48,120),
            (36,110),(36,100),(54,88),(70,68)]
    nodes = [(76,104),(114,78),(154,104),(112,124),(82,156),(140,158)]
    acc = "".join('<path class="acc" d="%s"/>' % circ(x,y,11,20+i,amt=1.2)
                  for i,(x,y) in enumerate(nodes)) + \
          '<path class="acc-line" d="M76,104 L114,78 L154,104 L112,124 Z ' \
          'M112,124 L82,156 M112,124 L140,158 M76,104 L112,124"/>'
    return I(curve(head,4,amt=2.2)), acc

def untangle():
    """A knot, and the single thread that pulls out of it."""
    return (I(scribble(96,120,46,seed=5),"ink-thin")
          + I(curve([(140,142),(176,152),(204,170),(210,186),(196,190),
                     (194,174),(212,168),(230,178)],6,False,amt=2.0),"ink-thin")), \
           A(circ(90,126,58,11,amt=5))

def growth():
    """Botanical - the quietest piece in the set."""
    leafL = [(126,128),(96,130),(70,112),(62,84),(92,78),(120,96)]
    leafR = [(132,112),(136,82),(164,62),(194,66),(190,96),(162,116)]
    return (I(curve([(112,226),(118,172),(126,120),(136,84)],7,False,amt=2.2))
          + I(curve(leafL,8,amt=2.0)) + I(curve(leafR,9,amt=2.0))
          + I(curve([(84,222),(128,226),(172,220)],12,False,amt=2.0),"ink-thin")), \
           ('<g class="acc" transform="translate(-9,9)">'
            + '<path d="%s"/><path d="%s"/></g>' % (curve(leafL,8,amt=2.0), curve(leafR,9,amt=2.0)))

def idea():
    """Old-world bulb. Filament drawn as one continuous stroke."""
    glass = [(128,34),(160,42),(184,66),(192,98),(182,126),(168,146),(163,168),(160,180),
             (96,180),(93,168),(88,146),(74,126),(64,98),(72,66),(96,42)]
    return (I(curve(glass,13,amt=2.2))
          + I(curve([(94,196),(162,196)],14,False,amt=1.6))
          + I(curve([(100,212),(156,212)],15,False,amt=1.6))
          + I(curve([(107,150),(112,122),(128,133),(144,122),(149,150)],16,False,amt=1.8),"ink-thin")), \
           A(circ(140,92,64,17,amt=5))

def artifacts():
    """Empty state: three sheets fanned out — a spreadsheet, a document and
    a slide. Each sheet gets a paper fill before its outline, so the one in
    front actually covers the one behind; stroke-only sheets let the back
    sheet's rules read straight through the front one."""
    import math

    def rect(cx, cy, w, h, deg):
        c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
        return [(cx + x*c - y*s, cy + x*s + y*c)
                for x, y in ((-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2))]

    def rule(C, x0, x1, y):
        cx, cy, w, h, deg = C
        c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
        return [(cx + (x*w/2)*c - (y*h/2)*s, cy + (x*w/2)*s + (y*h/2)*c)
                for x in (x0, x1)]

    def sheet(C, seed, detail):
        """Paper, then outline, then whatever is printed on it."""
        box = rect(*C)
        return (P(poly(box, seed, amt=2.0, bow=1.8))
                + I(poly(box, seed, amt=2.0, bow=1.8)) + detail(C)), box

    # Back left: the spreadsheet, tipped out of the fan.
    SC = (74, 132, 84, 112, -15)
    def grid(C):
        d = "".join(I(curve(rule(C, -.72, .72, y), 3005+i, False, amt=1.4), "ink-thin")
                    for i, y in enumerate((-.42, -.10, .22)))
        return d + "".join(I(curve([rule(C, x, x, -.70)[0], rule(C, x, x, .70)[0]],
                                   3010+i, False, amt=1.4), "ink-thin")
                           for i, x in enumerate((-.30, .10)))

    # Back right: the slide, tipped the other way.
    LC = (186, 136, 88, 106, 15)
    def slide(C):
        return (I(poly(rect(C[0]+2, C[1]-12, 54, 34, C[4]), 3020, amt=1.6, bow=1.4), "ink-thin")
                + I(curve(rule(C, -.58, .30, .40), 3022, False, amt=1.4), "ink-thin"))

    # Front centre: the document, upright and tallest, covering both.
    DC = (128, 142, 88, 124, 2)
    def doc(C):
        return "".join(I(curve(rule(C, -.66, w, y), 3030+i, False, amt=1.4), "ink-thin")
                       for i, (y, w) in enumerate(((-.54,.62),(-.34,.64),(-.14,.30),
                                                   (.06,.62),(.26,.40))))

    left,  boxS = sheet(SC, 3001, grid)
    right, boxL = sheet(LC, 3002, slide)
    front, boxD = sheet(DC, 3003, doc)

    # Fan order: the two behind first, the document over both.
    ink = left + right + front
    accent = A(poly([(x-9, y+9) for x, y in boxD], 3003, amt=2.0, bow=1.8))
    return ink, accent

def artifacts_hand():
    """Empty state: a hand offering a small sheaf of sheets. The hand is the
    hero - same comb-of-fingers construction as hand() - and the fingers come
    up IN FRONT of the paper, which is what makes it read as held rather than
    floating. A paper-filled palm blob sits between the sheaf and the ink so
    the sheets' ruling doesn't read through the hand."""
    import math

    def rect(cx, cy, w, h, deg):
        c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
        return [(cx + x*c - y*s, cy + x*s + y*c)
                for x, y in ((-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2))]

    def rule(C, x0, x1, y):
        cx, cy, w, h, deg = C
        c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
        return [(cx + (x*w/2)*c - (y*h/2)*s, cy + (x*w/2)*s + (y*h/2)*c)
                for x in (x0, x1)]

    def sheet(C, seed, detail):
        box = rect(*C)
        return (P(poly(box, seed, amt=2.0, bow=1.8))
                + I(poly(box, seed, amt=2.0, bow=1.8)) + detail(C)), box

    # Back left: the spreadsheet.
    SC = (92, 122, 74, 160, -14)
    def grid(C):
        return ("".join(I(curve(rule(C, -.70, .70, y), 3105+i, False, amt=1.4), "ink-thin")
                        for i, y in enumerate((-.56, -.40, -.24)))
                + "".join(I(curve([rule(C, x, x, -.66)[0], rule(C, x, x, -.10)[0]],
                                  3110+i, False, amt=1.4), "ink-thin")
                          for i, x in enumerate((-.26, .16))))

    # Back right: a slide, tipped the other way.
    LC = (178, 122, 74, 154, 14)
    def slide(C):
        return (I(poly(rect(C[0]+5, C[1]-34, 44, 30, C[4]), 3120, amt=1.6, bow=1.4), "ink-thin")
                + I(curve(rule(C, -.54, .26, -.20), 3122, False, amt=1.4), "ink-thin"))

    # Front centre: the document, tallest, covering both.
    DC = (134, 128, 80, 170, 2)
    def doc(C):
        return "".join(I(curve(rule(C, -.62, w, y), 3130+i, False, amt=1.4), "ink-thin")
                       for i, (y, w) in enumerate(((-.68,.58),(-.55,.60),(-.42,.24),
                                                   (-.29,.58),(-.16,.36))))

    left,  _ = sheet(SC, 3101, grid)
    right, _ = sheet(LC, 3102, slide)
    front, _ = sheet(DC, 3103, doc)

    # The hand: comb fingers rising in front of the sheaf, closed palm loop.
    # No thumb: hand() carries the motif on the comb and the closed palm loop
    # alone, and every thumb tried here read as a loop or a handle instead.
    palm = [(84,240),(76,220),(82,196),
            (90,188),(94,146),(104,146),(105,190),    # index
            (109,186),(113,130),(123,130),(125,186),    # middle, longest
            (129,186),(135,136),(144,137),(145,188),
            (149,192),(157,156),(166,158),(163,196),    # little finger, shortest
            (169,214),(165,230),(148,242),(120,246),(96,244)]
    # Opaque palm body, kept inside the ink loop, so the sheaf stops where the
    # hand starts instead of printing through it.
    mask = [(90,238),(84,208),(98,196),(140,194),(160,210),(158,228),(142,240),(106,244)]

    ink = (left + right + front
           + P(curve(mask, 3140, amt=2.0))
           + I(curve(palm, 3141, amt=2.0, t=.55)))
    accent = A(circ(176, 80, 64, 3150, amt=5))
    return ink, accent

PIECES = [("hand","Hand","kraft",hand),
          ("care","Cupped hands","manilla",care),
          ("reasoning","Reasoning","clay",reasoning),
          ("untangle","Untangle","kraft",untangle),
          ("growth","Growth","olive",growth),
          ("idea","Idea","manilla",idea),
          ("artifacts","Artifacts","clay",artifacts),
          ("artifacts-hand","Artifacts in hand","clay",artifacts_hand)]

# --------------------------------------------------------------- build
man = []
for i,(n,label,acc,fn) in enumerate(PIECES):
    ink, accent = fn()
    col  = render(n,      label, ink, accent, SW[acc], seed=i+40, sw=7.5, swt=5.5)
    mono = render(n+"-m", label, ink, "",     SW[acc], seed=i+40, sw=7.5, swt=5.5)
    open(os.path.join(DIR, n+".svg"), "w").write(col)
    open(os.path.join(DIR, n+"-mono.svg"), "w").write(mono)
    man.append({"name":n,"label":label,"acc":acc,"svg":col,"mono":mono})

grounds = ["manilla","ivoryD","cactus","kraft","ivoryM","oat"]
cards = "\n".join(
  '<figure class="card"><div class="art" style="--acc:%s;background:%s">%s</div>'
  '<figcaption><span class="k">Illustration</span><span class="t">%s</span></figcaption></figure>'
  % (SW[m["acc"]], SW[grounds[i%6]], m["svg"], m["label"]) for i,m in enumerate(man))
monos = "\n".join(
  '<figure class="card"><div class="art" style="background:%s">%s</div>'
  '<figcaption><span class="k">Ink only</span><span class="t">%s</span></figcaption></figure>'
  % (SW["ivoryM"], m["mono"], m["label"]) for m in man)

html = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Claude Illustrations</title><style>
:root{--slate:%(slate)s;--ivoryL:%(ivoryL)s;--ivoryM:%(ivoryM)s}
*{box-sizing:border-box}
body{margin:0;background:var(--ivoryL);color:var(--slate);
 font:400 18px/1.55 "Anthropic Serif",Georgia,serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:1080px;margin:0 auto;padding:72px 32px 120px}
h1{font-family:"Anthropic Sans",Arial,sans-serif;font-weight:700;letter-spacing:-.022em;
 font-size:clamp(2rem,5vw,3rem);margin:0 0 .35em;line-height:1.04}
h2{font-family:"Anthropic Sans",Arial,sans-serif;font-size:1.05rem;font-weight:600;margin:0 0 6px}
.sub{color:#87867f;font-size:.95rem;margin:0 0 24px;max-width:60ch}
.lede{max-width:56ch;font-size:1.25rem;color:#3d3d3a;margin:0}
.eyebrow{font-family:"Anthropic Sans",Arial,sans-serif;font-size:.72rem;font-weight:500;
 letter-spacing:.13em;text-transform:uppercase;color:#87867f;margin:0 0 18px}
hr{border:0;border-top:1px solid #1414131a;margin:56px 0}
.grid{display:grid;gap:22px;grid-template-columns:repeat(auto-fill,minmax(280px,1fr))}
.card{margin:0;background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 1px 2px #14141312}
.art{display:grid;place-items:center;padding:34px;aspect-ratio:4/3}
.art svg{width:min(210px,80%%);height:auto;display:block}
figcaption{padding:16px 18px 20px;display:flex;flex-direction:column;gap:3px}
.k{font:500 .68rem/1 "Anthropic Sans",Arial,sans-serif;letter-spacing:.09em;
 text-transform:uppercase;color:#87867f}
.t{font-family:"Anthropic Sans",Arial,sans-serif;font-weight:600;font-size:1rem}
ol.rules{max-width:62ch;padding-left:1.1em;margin:0}
ol.rules li{margin-bottom:.7em}
ol.rules b{font-family:"Anthropic Sans",Arial,sans-serif;font-weight:600}
</style></head><body><div class="wrap">
<p class="eyebrow">Concept app &middot; illustration language</p>
<h1>Claude illustrations</h1>
<p class="lede">The larger tier. Same hand as the icon set, thinner relative line,
composed rather than contained &mdash; for blog cards, empty states, headers and spot art.</p>

<hr><h2>Spot illustrations</h2>
<p class="sub">Each on one of Anthropic's swatch grounds, the way the blog cards run.</p>
<div class="grid">%(cards)s</div>

<hr><h2>Ink only</h2>
<p class="sub">The same six with the paper shape withheld.</p>
<div class="grid">%(monos)s</div>

<hr><h2>How this tier differs from the icons</h2>
<ol class="rules">
<li><b>Thinner relative line.</b> 7.5 units against the icon set's 11, on the same
256 grid. Illustrations are read large; an icon's weight looks clumsy there.</li>
<li><b>Composed, not contained.</b> An icon fills its box evenly. An illustration
can sit off-centre, run out of frame, and leave the ground doing real work.</li>
<li><b>Humanistic motifs first.</b> Hands above all &mdash; they carry the
human&ndash;AI collaboration idea that the whole identity rests on. Then profiles,
bulbs, books, botanicals, knots, node constellations.</li>
<li><b>The ground is part of the drawing.</b> These are built for full swatch
fields, not for white cards.</li>
<li><b>Same non-negotiables.</b> One accent, misregistered, behind the line. No
shadows, no gradients, no second outline. Must read with the accent removed.</li>
</ol>
</div></body></html>""" % {"slate":SW["slate"],"ivoryL":SW["ivoryL"],"ivoryM":SW["ivoryM"],
                           "cards":cards,"monos":monos}

open(os.path.join(DIR, "index.html"), "w").write(html)
print("wrote", len(man), "illustrations (colour + mono) ->", DIR)
