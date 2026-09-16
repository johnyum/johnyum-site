import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from draw import SW, jit, curve, poly, circ, scribble, I, A, S, render


def green_egg():
    """Kamado with the lid swung open on its hinge - not the closed dome."""
    bowl=[(44,138),(52,184),(86,216),(128,224),(170,216),(204,184),(212,138)]
    lid=[(64,88),(76,36),(132,12),(186,26),(206,68),(138,74)]
    return (I(curve(bowl,1800,False))
          + I(curve([(38,138),(128,146),(218,138)],1801,False))
          + I(curve(lid,1802))
          + I(curve([(204,76),(214,132)],1803,False))
          + I(curve([(66,226),(56,244),(200,244),(190,226)],1804,False),"ink-thin")), \
           A(curve([(x-8,y+8) for x,y in bowl],1805,amt=4))


def guest():
    """A door with a welcome mat."""
    door=[(66,28),(190,28),(190,204),(66,204)]
    return (I(poly(door,1806))
          + I(circ(162,120,11,1807),"ink-thin")
          + I(poly([(78,212),(178,212),(212,240),(44,240)],1808))
          + I(curve([(84,226),(172,226)],1809,False),"ink-thin")), \
           A(poly([(x-8,y+8) for x,y in door],1810,bow=3))


def home_buying():
    """A key whose bow is a little house - mortgages and offers."""
    head=[(28,102),(80,56),(132,102),(132,158),(28,158)]
    return (I(poly(head,1811))
          + I(circ(80,128,15,1812),"ink-thin")
          + I(curve([(132,130),(236,130)],1813,False))
          + I(curve([(198,130),(198,166)],1814,False))
          + I(curve([(232,130),(232,160)],1815,False))), \
           A(poly([(x-8,y+8) for x,y in head],1816,bow=3))


def homes():
    """House section mark - wide eaves, chimney, one door."""
    walls=[(52,112),(204,112),(204,224),(52,224)]
    return (I(poly([(24,122),(128,34),(232,122)],1817,False))
          + I(poly(walls,1818))
          + I(poly([(172,68),(196,68),(196,92)],1819,False))
          + I(poly([(104,224),(104,160),(152,160),(152,224)],1820,False))), \
           A(poly([(x-8,y+8) for x,y in walls],1821,bow=3))


def hose():
    """A coiled garden hose running out to a spray nozzle."""
    spiral=[(148,118),(102,112),(78,140),(106,168),(150,160),(178,130),(170,90),(120,66),
            (64,82),(34,130),(54,186),(110,216),(168,200),(196,158),(206,120)]
    return (I(curve(spiral,1822,False))
          + I(poly([(198,114),(240,66),(254,92),(212,128)],1823))), \
           A(circ(96,146,80,1826,amt=5))


def hotel():
    """Hotel block with a striped awning over the entrance."""
    block=[(54,26),(202,26),(202,236),(54,236)]
    win="".join(I(poly([(x,62),(x+42,62),(x+42,104),(x,104)],1827+i),"ink-thin")
                for i,x in enumerate((78,136)))
    return (I(poly(block,1829))
          + win
          + I(poly([(70,152),(186,152),(206,182),(50,182)],1830))
          + I(curve([(108,152),(96,182)],1831,False),"ink-thin")
          + I(curve([(148,152),(160,182)],1832,False),"ink-thin")
          + I(poly([(104,236),(104,190),(152,190),(152,236)],1833,False))), \
           A(poly([(x-8,y+8) for x,y in block],1834,bow=3))


def knee():
    """Bent leg with a support wrap - the foot is what stops it reading as pipe."""
    leg=[(40,24),(160,80),(198,124),(154,182),(132,216),(132,242),(30,242),(28,216),
         (100,198),(112,172),(142,114),(40,72)]
    return (I(curve(leg,1835,amt=2.2,t=0.45))
          + I(curve([(174,72),(128,114)],1836,False),"ink-thin")
          + I(curve([(204,118),(152,158)],1837,False),"ink-thin")), \
           A(curve([(x-8,y+8) for x,y in leg],1838,amt=3,t=0.45))


def life_stuff():
    """A sparkle - the loose catch-all."""
    star=[(128,20),(152,104),(236,128),(152,152),(128,236),(104,152),(20,128),(104,104)]
    return I(curve(star,1839,amt=2.4,t=0.5)), \
           A(curve([(x-8,y+8) for x,y in star],1840,amt=3,t=0.5))


def magnifier():
    return (I(circ(106,106,70,1841))
          + I(curve([(158,158),(220,220)],1842,False))), \
           A(circ(98,114,70,1843,amt=5))


def map_():
    """Folded paper map with a route running across it."""
    sheet=[(26,58),(96,38),(160,62),(230,42),(230,194),(160,214),(96,190),(26,210)]
    return (I(curve(sheet,1844,amt=2.2,t=0.45))
          + I(curve([(96,38),(96,190)],1845,False),"ink-thin")
          + I(curve([(160,62),(160,214)],1846,False),"ink-thin")
          + I(curve([(58,168),(92,118),(142,146),(196,88)],1847,False))), \
           A(curve([(x-8,y+8) for x,y in sheet],1848,amt=3,t=0.45))


ICONS = [("green-egg","Kamado grill","olive",green_egg),
         ("guest","Guest","kraft",guest),
         ("home-buying","Home buying","manilla",home_buying),
         ("homes","Homes","clay",homes),
         ("hose","Garden hose","cactus",hose),
         ("hotel","Hotel","fig",hotel),
         ("knee","Knee","heather",knee),
         ("life-stuff","Life stuff","accent",life_stuff),
         ("magnifier","Magnifier","oat",magnifier),
         ("map","Map","olive",map_)]
