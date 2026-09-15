import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

OUT=os.path.dirname(os.path.abspath(__file__))
ICODIR=os.path.join(OUT,"icons")
os.makedirs(ICODIR,exist_ok=True)

from draw import SW, W, jit, curve, poly, circ, scribble, I, A, S, render

# ---------------------------------------------------------------- the 12
def big_green_egg():
    body=[(128,50),(178,64),(206,104),(210,148),(190,188),(150,206),(106,206),(66,188),(46,148),(50,104),(78,64)]
    ink=(I(curve(body,1))
       + I(curve([(50,120),(128,128),(208,120)],2,False),"ink")
       + I(poly([(112,52),(144,52),(138,28),(118,28)],3))
       + I(poly([(74,204),(60,232),(196,232),(182,204)],4,False),"ink-thin"))
    return ink, A(curve([(128,50),(178,64),(206,104),(210,148),(190,188),(150,206),(106,206),(66,188),(46,148),(50,104),(78,64)],9,amt=4))

def brisket():
    slab=[(42,152),(50,116),(78,94),(128,86),(180,90),(212,110),(222,144),(214,172),
          (150,178),(92,178),(50,174)]
    return (I(curve(slab,5))
          + I(curve([(50,120),(96,102),(152,98),(210,114)],6,False),"ink-thin")
          + I(curve([(88,108),(84,176)],7,False),"ink-thin")
          + I(curve([(126,100),(124,178)],8,False),"ink-thin")), A(curve([(x-8,y+8) for x,y in slab],11,amt=4))

def golf():
    flag=[(152,38),(74,62),(152,92)]
    return (I(curve([(152,32),(150,124),(148,200)],10,False))
          + I(poly(flag,9))
          + I(curve([(46,208),(128,218),(214,206)],11,False),"ink-thin")
          + I(curve([(124,200),(148,206),(172,199),(148,193)],12)) ), \
           A(poly([(x-8,y+8) for x,y in flag],13,bow=3))

def catan():
    hexa=[(128,34),(206,80),(206,170),(128,216),(50,170),(50,80)]
    return (I(poly(hexa,14))+I(circ(128,126,38,15))), A(poly([(x-8,y+8) for x,y in hexa],16,bow=3))

def porsche():
    body=[(24,166),(30,138),(56,130),(84,100),(122,82),(158,86),(188,106),(216,126),(234,142),
          (236,162),(228,174),(28,174)]
    return (I(curve(body,17))
          + I(curve([(90,106),(126,94),(156,104)],18,False),"ink-thin")
          + I(circ(74,174,25,19))+I(circ(184,174,25,20))), A(curve([(x-8,y+8) for x,y in body],21,amt=4))

def plane():
    p=[(128,24),(142,62),(148,102),(216,148),(216,170),(148,152),(150,192),(178,214),(178,228),
       (128,214),(78,228),(78,214),(106,192),(108,152),(40,170),(40,148),(108,102),(114,62)]
    return I(curve(p,22,amt=2.2,t=0.55)), A(curve([(x-8,y+8) for x,y in p],23,amt=3,t=0.55))

def wine():
    bowl=[(80,38),(176,38),(172,98),(128,142),(84,98)]
    return (I(curve(bowl,24))
          + I(curve([(128,142),(128,198)],25,False))
          + I(curve([(88,202),(128,210),(168,202)],26,False))), A(curve([(88,66),(168,66),(164,100),(128,136),(92,100)],27,amt=3))

def dumpling():
    body=[(52,170),(58,126),(86,96),(128,86),(170,96),(198,126),(204,170),(170,184),(128,190),(86,184)]
    return (I(curve(body,28))
          + I(curve([(82,99),(92,128)],29,False),"ink-thin")
          + I(curve([(127,88),(129,120)],30,False),"ink-thin")
          + I(curve([(172,99),(163,128)],31,False),"ink-thin")), A(curve([(x-8,y+8) for x,y in body],32,amt=4))

def camera():
    body=[(32,82),(88,82),(102,54),(154,54),(168,82),(224,82),(224,198),(32,198)]
    return (I(poly(body,33))+I(circ(128,140,40,34))
          + I(circ(62,104,7,35),"ink-thin")), A(poly([(x-8,y+8) for x,y in body],36,bow=3))

def palm():
    fr=lambda a,b,s: I(curve(a,s,False)) if 0 else None
    fronds=(I(curve([(134,78),(96,46),(46,50)],37,False))
          + I(curve([(134,78),(86,84),(50,116)],38,False))
          + I(curve([(134,78),(180,44),(224,54)],39,False))
          + I(curve([(134,78),(188,90),(216,122)],40,False))
          + I(curve([(134,78),(132,40),(112,20)],41,False)))
    return (I(curve([(112,226),(118,172),(126,120),(136,84)],42,False))
          + fronds), A(circ(138,76,58,43,amt=6))

def watch():
    return (I(poly([(94,84),(94,30),(162,30),(162,84)],44,False))
          + I(poly([(94,172),(94,226),(162,226),(162,172)],45,False))
          + I(circ(128,128,54,46))
          + I(curve([(128,128),(128,94)],47,False),"ink-thin")
          + I(curve([(128,128),(160,146)],48,False),"ink-thin")), A(circ(136,120,54,49,amt=5))

def dice():
    sq=[(58,58),(198,58),(198,198),(58,198)]
    pips="".join('<path class="solid" d="%s"/>'%circ(x,y,13,60+i,amt=1.4)
                 for i,(x,y) in enumerate([(94,94),(162,94),(128,128),(94,162),(162,162)]))
    return I(poly(sq,50))+pips, A(poly([(x-8,y+8) for x,y in sq],51,bow=3))

ICONS=[("big-green-egg","Big Green Egg","olive",big_green_egg),
       ("brisket","Brisket","clay",brisket),
       ("golf-flag","Golf flag","accent",golf),
       ("catan","Catan hex","cactus",catan),
       ("porsche","Porsche 911","clay",porsche),
       ("plane","Plane","heather",plane),
       ("wine","Wine","fig",wine),
       ("dumpling","Dumpling","manilla",dumpling),
       ("camera","Camera","oat",camera),
       ("palm","Palm","olive",palm),
       ("watch","Watch","kraft",watch),
       ("dice","Dice","clay",dice)]

MONODIR=os.path.join(OUT,"icons-mono")
os.makedirs(MONODIR,exist_ok=True)

man=[]
for i,(n,label,acc,fn) in enumerate(ICONS):
    ink,accent=fn()
    col =render(n,      label, ink, accent, SW[acc], seed=i)
    mono=render(n+"-m", label, ink, "",     SW[acc], seed=i)
    open(os.path.join(ICODIR,n+".svg"),"w").write(col)
    open(os.path.join(MONODIR,n+".svg"),"w").write(mono)
    man.append({"name":n,"label":label,"acc":acc,"svg":col,"mono":mono})

# ---------------------------------------------------------------- gallery
gr=["ivoryM","ivoryD","ivoryL"]
def tile(m,i,key="svg",ground=None):
    return ('<figure class="tile" style="--acc:%s;--ground:%s"><div class="art">%s</div>'
            '<figcaption><span class="nm">%s</span><span class="sw">%s</span></figcaption></figure>'
            %(SW[m["acc"]], ground or SW[gr[i%3]], m[key], m["label"],
              m["acc"] if key=="svg" else "slate"))

grid_col ="\n".join(tile(m,i) for i,m in enumerate(man))
grid_mono="\n".join(tile(m,i,"mono",SW["ivoryM"]) for i,m in enumerate(man))

def at(m,px,key="svg"):
    return ('<div class="mini" style="--acc:%s">%s<span>%s</span></div>'
            %(SW[m["acc"]], m[key].replace('viewBox','width="%d" height="%d" viewBox'%(px,px),1),
              m["label"]))

s32  ="".join(at(m,32) for m in man)
s32m ="".join(at(m,32,"mono") for m in man)
s20  ="".join(at(m,20,"mono") for m in man)
ramp ="".join('<div class="mini" style="--acc:%s">%s<span>%s</span></div>'%(
        SW[man[0]["acc"]], man[0]["svg"].replace('viewBox','width="%d" height="%d" viewBox'%(px,px),1), px)
        for px in (96,64,48,32,24,20))
sws  ="".join('<li><i style="background:%s"></i><b>%s</b><code>%s</code></li>'%(v,k,v)
              for k,v in SW.items() if k!="ivoryL")

html="""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Claude Icon Set</title><style>
:root{--slate:%(slate)s;--ivoryL:%(ivoryL)s;--ivoryM:%(ivoryM)s;--ivoryD:%(ivoryD)s}
*{box-sizing:border-box}
body{margin:0;background:var(--ivoryL);color:var(--slate);
 font:400 18px/1.55 "Anthropic Serif",Georgia,serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:1080px;margin:0 auto;padding:72px 32px 120px}
h1{font-family:"Anthropic Sans",Arial,sans-serif;font-weight:700;letter-spacing:-.022em;
 font-size:clamp(2rem,5vw,3rem);margin:0 0 .35em;line-height:1.04}
h2{font-family:"Anthropic Sans",Arial,sans-serif;font-size:1.05rem;font-weight:600;margin:0 0 6px}
.sub{color:#87867f;font-size:.95rem;margin:0 0 22px;max-width:60ch}
.lede{max-width:56ch;font-size:1.25rem;color:#3d3d3a;margin:0}
.eyebrow{font-family:"Anthropic Sans",Arial,sans-serif;font-size:.72rem;font-weight:500;
 letter-spacing:.13em;text-transform:uppercase;color:#87867f;margin:0 0 18px}
hr{border:0;border-top:1px solid #1414131a;margin:56px 0}
.grid{display:grid;gap:18px;grid-template-columns:repeat(auto-fill,minmax(190px,1fr))}
.tile{margin:0;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 1px 2px #14141312;
 transition:transform .18s ease}
.tile:hover{transform:translateY(-3px)}
.art{background:var(--ground);display:grid;place-items:center;padding:24px}
.art svg{width:112px;height:112px;display:block}
figcaption{display:flex;justify-content:space-between;align-items:baseline;gap:8px;padding:13px 15px 15px}
.nm{font-family:"Anthropic Sans",Arial,sans-serif;font-weight:600;font-size:.92rem}
.sw{font-size:.68rem;letter-spacing:.07em;text-transform:uppercase;color:#87867f;
 font-family:"Anthropic Sans",Arial,sans-serif}
.strip{display:flex;flex-wrap:wrap;gap:10px;background:var(--ivoryM);border-radius:12px;padding:22px}
.strip.dark{background:var(--slate)}
.strip.dark .mini span{color:#b0aea5}
.strip.dark .ink,.strip.dark .ink-thin{stroke:var(--ivoryL)}
.strip.dark .solid{fill:var(--ivoryL)}
.mini{width:88px;display:flex;flex-direction:column;align-items:center;gap:9px;padding:10px 4px}
.mini svg{display:block}
.mini span{font:500 .64rem/1.2 "Anthropic Sans",Arial,sans-serif;color:#87867f;text-align:center}
.ramp{align-items:flex-end}
ul.sws{list-style:none;padding:0;margin:0;display:grid;gap:10px;
 grid-template-columns:repeat(auto-fill,minmax(160px,1fr))}
ul.sws li{display:flex;align-items:center;gap:10px;font-size:.85rem}
ul.sws i{width:26px;height:26px;border-radius:6px;flex:none;box-shadow:inset 0 0 0 1px #14141314}
ul.sws b{font-family:"Anthropic Sans",Arial,sans-serif;font-weight:500}
ul.sws code{color:#87867f;font-size:.74rem;margin-left:auto}
ol.rules{max-width:62ch;padding-left:1.1em;margin:0}
ol.rules li{margin-bottom:.7em}
ol.rules b{font-family:"Anthropic Sans",Arial,sans-serif;font-weight:600}
</style></head><body><div class="wrap">

<p class="eyebrow">Concept app &middot; icon language</p>
<h1>Claude icon set</h1>
<p class="lede">Twelve subjects from the app lineup, drawn in Anthropic's illustration
language: one measured ink line, a flat paper shape misregistered behind it, and the warm
swatch palette read live from anthropic.com. Ships in two cuts &mdash; colour and ink&nbsp;only.</p>

<hr><h2>Colour</h2><p class="sub">Twelve icons &middot; 256 grid &middot; one accent each.</p>
<div class="grid">%(gc)s</div>

<hr><h2>Ink only</h2>
<p class="sub">The same twelve with the paper shape withheld. This is the cut for dense UI,
print, stamps, and anywhere the accent would compete &mdash; and it is the honest test of
whether the drawing carries the meaning on its own.</p>
<div class="grid">%(gm)s</div>

<hr><h2>32&thinsp;px</h2><p class="sub">Actual size. Every icon has to survive here.</p>
<div class="strip">%(s32)s</div>
<p class="sub" style="margin:12px 0 0">Ink only.</p>
<div class="strip" style="margin-top:8px">%(s32m)s</div>
<p class="sub" style="margin:12px 0 0">Inverted to ivory on slate.</p>
<div class="strip dark" style="margin-top:8px">%(s32)s</div>

<hr><h2>20&thinsp;px</h2><p class="sub">Past the floor &mdash; where the set starts to give out.</p>
<div class="strip">%(s20)s</div>

<hr><h2>Size ramp</h2><p class="sub">One icon from 96 down to 20.</p>
<div class="strip ramp">%(ramp)s</div>

<hr><h2>Palette</h2><p class="sub">Read live from anthropic.com CSS variables.</p>
<ul class="sws">%(sws)s</ul>

<hr><h2>Rules that hold the set together</h2>
<ol class="rules">
<li><b>One ink weight.</b> 11 units on a 256 grid for every contour, 8.5 for interior
detail. Round caps and joins. The line never tapers.</li>
<li><b>A measured hand, not a shaky one.</b> Anchors are nudged off true and edges bowed
before any noise filter runs &mdash; but the amplitude is held low on purpose. Push the
wobble further and the set reads as a child's drawing instead of a considered one.</li>
<li><b>The paper shape misregisters.</b> One flat accent per icon, unoutlined, offset down
and left like a colour plate that slipped on press. Behind the line, never filling it.</li>
<li><b>Every icon must work without its accent.</b> If the ink-only cut above is ambiguous,
the drawing is wrong &mdash; colour is not allowed to carry meaning.</li>
<li><b>No shadows, no gradients, no second outline.</b> That is what keeps this set distinct
from the <em>playful</em> clay set &mdash; never mix the two.</li>
<li><b>Built for 32.</b> Nothing thinner than 8.5, no gap under 20 units, and detail earns
its place only if it survives the strip above. A subject that needs fine internal structure
gets swapped, not thinned &mdash; which is why the driver became a flag.</li>
<li><b>Warm grounds.</b> These are drawn for ivory and swatch tiles, not for white.</li>
</ol>

</div></body></html>"""%{"slate":SW["slate"],"ivoryL":SW["ivoryL"],"ivoryM":SW["ivoryM"],
  "ivoryD":SW["ivoryD"],"gc":grid_col,"gm":grid_mono,"s32":s32,"s32m":s32m,"s20":s20,
  "ramp":ramp,"sws":sws}

open(os.path.join(OUT,"index.html"),"w").write(html)
print("wrote",len(man),"colour +",len(man),"mono")
