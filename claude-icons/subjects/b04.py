import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from draw import SW, jit, curve, poly, circ, scribble, I, A, S, render


def family_tree():
    top=(128,52,30)
    return (I(circ(*top,1600))
          + I(circ(72,190,30,1601))
          + I(circ(184,190,30,1602))
          + I(curve([(128,82),(128,122)],1603,False))
          + I(curve([(72,122),(128,124),(184,122)],1604,False))
          + I(curve([(72,122),(72,160)],1605,False))
          + I(curve([(184,122),(184,160)],1606,False))), \
           A(circ(120,60,30,1607,amt=4)
             + " " + circ(64,198,30,1608,amt=4)
             + " " + circ(176,198,30,1609,amt=4))


def film():
    body=[(28,100),(228,100),(228,218),(28,218)]
    bar=[(30,58),(224,40),(230,84),(36,102)]
    stripes="".join(I(curve(p,1610+i,False)) for i,p in enumerate([
        [(86,50),(72,96)],[(148,44),(134,90)],[(210,42),(196,84)]]))
    return (I(poly(bar,1613))
          + stripes
          + I(poly(body,1614))), \
           A(poly([(x-8,y+8) for x,y in body],1615,bow=3))


def fish():
    body=[(34,128),(76,92),(138,84),(190,106),(212,128),(190,152),(138,172),(76,164)]
    return (I(curve(body,1616))
          + I(curve([(210,104),(242,88),(234,128),(242,168),(210,152)],1617,False))
          + I(circ(78,116,8,1618),"ink-thin")
          + I(curve([(112,90),(128,116),(112,142)],1619,False),"ink-thin")), \
           A(curve([(x-8,y+8) for x,y in body],1620,amt=4))


def fortnite():
    body=[(58,124),(96,108),(146,106),(168,124),(164,162),(120,170),(62,164)]
    legs="".join(I(curve([(x,160),(x,206)],1621+i,False))
                 for i,x in enumerate([(76),(104),(132),(156)]))
    return (I(curve(body,1625))
          + legs
          + I(poly([(136,124),(168,120),(186,66),(154,60)],1626))
          + I(curve([(170,68),(196,54),(212,66),(196,86),(168,88)],1627))
          + I(curve([(164,44),(158,22)],1628,False))
          + I(curve([(192,42),(200,22)],1629,False))
          + I(curve([(58,134),(28,112)],1630,False))
          + I(curve([(66,140),(158,136)],1675,False),"ink-thin")), \
           A(curve([(x-8,y+8) for x,y in body],1676,amt=4))


def fridge():
    body=[(62,18),(194,18),(194,238),(62,238)]
    return (I(poly(body,1631))
          + I(curve([(64,98),(128,100),(192,98)],1632,False))
          + I(curve([(168,44),(168,84)],1633,False))
          + I(curve([(168,116),(168,168)],1634,False))), \
           A(poly([(x-8,y+8) for x,y in body],1635,bow=3))


def gaming():
    body=[(56,102),(102,88),(156,88),(202,102),(220,146),(206,182),(178,178),(152,154),
          (106,154),(80,178),(52,182),(38,146)]
    return (I(curve(body,1636))
          + I(curve([(68,124),(104,124)],1637,False),"ink-thin")
          + I(curve([(86,106),(86,142)],1638,False),"ink-thin")
          + I(circ(166,112,10,1639),"ink-thin")
          + I(circ(196,138,10,1640),"ink-thin")), \
           A(curve([(x-8,y+8) for x,y in body],1641,amt=4))


def gate():
    arch=[(34,220),(34,96),(66,54),(128,38),(190,54),(222,96),(222,220)]
    bars="".join(I(curve([(x,y),(x,214)],1642+i,False)) for i,(x,y) in enumerate(
        [(78,62),(128,42),(178,62)]))
    return (I(curve(arch,1645,False))
          + bars
          + I(curve([(34,140),(128,134),(222,140)],1646,False))
          + I(curve([(20,232),(128,238),(236,232)],1647,False))), \
           A(curve([(x-8,y+8) for x,y in arch],1648,False,amt=4))


def golf():
    bag=[(76,102),(180,98),(188,212),(184,234),(74,238),(68,212)]
    clubs="".join(I(curve(p,1665+i,False)) for i,p in enumerate([
        [(100,100),(74,30)],[(128,98),(126,18)],[(158,100),(186,32)]]))
    return (clubs
          + I(curve(bag,1671))
          + I(curve([(72,150),(184,146)],1672,False),"ink-thin")
          + I(curve([(76,186),(184,182)],1677,False),"ink-thin")), \
           A(curve([(x-8,y+8) for x,y in bag],1673,amt=4))


def golf_ball():
    ball=(128,104,62)
    dimples="".join(I(circ(x,y,8,1653+i),"ink-thin") for i,(x,y) in enumerate(
        [(100,74),(142,64),(114,114),(156,104)]))
    return (I(circ(*ball,1674))
          + dimples
          + I(poly([(100,166),(156,166),(142,226),(114,226)],1657))
          + I(curve([(80,240),(128,246),(176,240)],1658,False))), \
           A(circ(120,112,62,1659,amt=5))


def golf_club():
    head=[(34,180),(116,148),(136,192),(58,222)]
    return (I(curve([(212,24),(166,96),(126,160)],1660,False))
          + I(poly(head,1661))
          + I(curve([(74,168),(92,208)],1662,False),"ink-thin")
          + I(curve([(206,18),(226,32)],1663,False),"ink-thin")), \
           A(poly([(x-8,y+8) for x,y in head],1664,bow=3))


ICONS = [("family-tree","Family tree","heather",family_tree),
         ("film","Film","oat",film),
         ("fish","Fish","cactus",fish),
         ("fortnite","Fortnite llama","fig",fortnite),
         ("fridge","Fridge","cactus",fridge),
         ("gaming","Gaming","heather",gaming),
         ("gate","Gate","kraft",gate),
         ("golf","Golf","olive",golf),
         ("golf-ball","Golf ball","manilla",golf_ball),
         ("golf-club","Golf club","clay",golf_club)]
