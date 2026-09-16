import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from draw import SW, jit, curve, poly, circ, scribble, I, A, S, render

OFF = lambda pts, dx=-8, dy=8: [(x+dx, y+dy) for x, y in pts]


def car():
    """Ordinary hatchback, side three-quarter. Upright tail, not a 911."""
    body=[(24,172),(26,132),(54,124),(80,80),(150,76),(188,112),(196,134),(234,138),(234,172)]
    return (I(poly(body,1200,bow=2.6))
          + I(poly([(72,118),(92,88),(146,86),(176,118)],1201,False),"ink-thin")
          + I(curve([(126,86),(128,118)],1202,False),"ink-thin")
          + I(circ(74,172,26,1203))+I(circ(186,172,26,1204))), \
           A(poly(OFF(body),1205,bow=3))


def carseat():
    """Flared bucket shell, narrow carry handle, five-point buckle."""
    shell=[(30,106),(226,106),(210,164),(168,194),(88,194),(46,164)]
    return (I(poly(shell,1210,bow=2.6))
          + I(curve([(74,106),(90,52),(128,36),(166,52),(182,106)],1211,False))
          + I(curve([(70,122),(158,180)],1212,False),"ink-thin")
          + I(curve([(186,122),(98,180)],1213,False),"ink-thin")
          + I(circ(128,151,13,1214),"ink-thin")), \
           A(poly(OFF(shell),1215,bow=3))


def cash():
    """Three banknotes fanned about a common corner."""
    def note(a, s):
        r = math.radians(a); ox, oy = 46, 184
        pts=[(0,0),(168,0),(168,-60),(0,-60)]
        return [(ox + x*math.cos(r) + y*math.sin(r),
                 oy - x*math.sin(r) + y*math.cos(r)) for x, y in pts]
    front = note(0, 1220)
    return (I(poly(note(30,0),1220,bow=2.6))
          + I(poly(note(15,0),1221,bow=2.6))
          + I(poly(front,1222,bow=2.6))
          + I(circ(130,154,19,1223),"ink-thin")), \
           A(poly(OFF(front),1224,bow=3))


def charcoal():
    left =[(28,198),(42,150),(86,136),(116,170),(104,198)]
    right=[(120,198),(136,158),(178,140),(212,170),(204,198)]
    top  =[(80,140),(108,102),(152,96),(170,132),(126,148)]
    return (I(poly(top,1230,bow=2.6))
          + I(poly(left,1231,bow=2.6))
          + I(poly(right,1232,bow=2.6))
          + S(circ(176,166,11,1233,amt=1.4))), \
           A(poly(OFF([(28,198),(42,150),(80,140),(108,102),(152,96),(170,132),
                       (178,140),(212,170),(204,198)]),1234,bow=3))


def chicken():
    meat=[(62,198),(46,160),(56,116),(92,86),(136,84),(166,112),(168,154),(138,188),(96,204)]
    return (I(curve(meat,1240))
          + I(curve([(146,116),(196,68)],1241,False))
          + I(circ(186,54,18,1242))
          + I(circ(210,78,18,1243))), \
           A(curve(OFF(meat),1244,amt=4))


def chips():
    bag=[(76,234),(64,148),(192,148),(180,234)]
    return (I(curve([(46,138),(80,74),(116,126)],1253,t=0.8))
          + I(curve([(136,132),(174,70),(208,122)],1254,t=0.8))
          + I(poly(bag,1250,bow=2.6))
          + I(poly([(62,150),(88,106),(116,148),(146,102),(174,144),(194,150)],1251,False))
          + I(curve([(76,198),(180,198)],1252,False),"ink-thin")), \
           A(poly(OFF(bag),1254,bow=3))


def clock():
    return (I(circ(128,130,84,1260))
          + I(curve([(128,130),(128,76)],1261,False),"ink-thin")
          + I(curve([(128,130),(174,152)],1262,False),"ink-thin")
          + I(poly([(112,34),(144,34)],1263,False),"ink-thin")), \
           A(circ(120,138,84,1264,amt=5))


def coast():
    land=[(14,172),(14,94),(54,78),(106,84),(142,98),(158,140),(150,172)]
    return (I(poly(land,1270,bow=2.6))
          + I(curve([(30,202),(64,190),(98,202),(132,190),(166,202),(200,190),(232,200)],1271,False))
          + I(curve([(40,234),(74,222),(108,234),(142,222),(176,234),(210,222),(238,232)],1272,False))), \
           A(poly(OFF(land),1273,bow=3))


def concrete():
    face=[(26,170),(214,170),(214,210),(26,210)]
    blade=[(38,112),(178,66),(140,128)]
    return (I(poly(face,1280,bow=2.6))
          + I(poly([(26,170),(48,152),(236,152),(214,170)],1281,bow=2.6))
          + I(poly(blade,1282,bow=2.6))
          + I(curve([(126,94),(180,42)],1283,False))
          + I(circ(196,28,16,1284))), \
           A(poly(OFF(face),1285,bow=3))


def contract():
    page=[(44,24),(172,24),(172,200),(44,200)]
    return (I(poly(page,1290,bow=2.6))
          + I(curve([(68,66),(148,66)],1291,False),"ink-thin")
          + I(curve([(68,96),(148,96)],1292,False),"ink-thin")
          + I(curve([(68,126),(124,126)],1293,False),"ink-thin")
          + I(curve([(64,166),(82,148),(96,172),(114,144),(132,168),(148,154)],1294,False))
          + I(circ(178,190,30,1295))
          + I(circ(178,190,13,1296),"ink-thin")), \
           A(poly(OFF(page),1297,bow=3))


ICONS = [("car","Car","heather",car),
         ("carseat","Car seat","cactus",carseat),
         ("cash","Cash","olive",cash),
         ("charcoal","Charcoal","manilla",charcoal),
         ("chicken","Chicken","kraft",chicken),
         ("chips","Chips","oat",chips),
         ("clock","Clock","fig",clock),
         ("coast","Coast","cactus",coast),
         ("concrete","Concrete","oat",concrete),
         ("contract","Contract","clay",contract)]
