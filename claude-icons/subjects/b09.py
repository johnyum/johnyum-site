import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from draw import SW, jit, curve, poly, circ, scribble, I, A, S, render


def style():
    """A t-shirt - the section mark for clothes. A sneaker in profile reads as a blob."""
    shirt=[(88,46),(128,62),(168,46),(214,80),(188,116),(172,102),(172,216),(84,216),
           (84,102),(68,116),(42,80)]
    return (I(poly(shirt,2600,bow=1.6))
          + I(curve([(98,50),(128,74),(158,50)],2601,False),"ink-thin")), \
           A(poly([(x-8,y+8) for x,y in shirt],2604,bow=2.4))


def tag():
    """A price tag: pointed crown, punched hole, a string looped through."""
    body=[(68,74),(128,26),(188,74),(188,212),(68,212)]
    return (I(poly(body,2605))
          + I(circ(128,80,17,2606))
          + I(curve([(108,34),(120,8),(150,14),(146,40)],2607,False),"ink-thin")
          + I(curve([(92,148),(164,148)],2608,False),"ink-thin")), \
           A(poly([(x-8,y+8) for x,y in body],2609,bow=3))


def teak():
    """A slatted teak chair, front on. Wide slats - narrow ones read as chocolate."""
    back=[(58,26),(198,26),(198,142),(58,142)]
    slats="".join(I(curve([(64,y),(128,y+2),(192,y)],2610+i,False))
                  for i,y in enumerate((64,102)))
    legs="".join(I(curve([(x,178),(x+d,232)],2612+i,False))
                 for i,(x,d) in enumerate(((66,-8),(190,8))))
    return (I(poly(back,2614))
          + slats
          + I(poly([(38,142),(218,142),(218,178),(38,178)],2615))
          + legs), \
           A(poly([(x-8,y+8) for x,y in back],2616,bow=3))


def thermometer():
    """An instant-read probe: round dial, long stem, pointed tip."""
    return (I(circ(128,68,50,2617))
          + I(curve([(128,68),(158,44)],2618,False),"ink-thin")
          + I(curve([(92,150),(164,150)],2619,False))
          + I(curve([(128,150),(128,238)],2620,False))), \
           A(circ(120,76,50,2621,amt=5))


def ticket():
    """A torn admission stub - V notches and a perforation line."""
    body=[(28,56),(166,56),(180,78),(194,56),(228,56),(228,200),(194,200),(180,178),
          (166,200),(28,200)]
    return (I(poly(body,2622))
          + I(curve([(180,100),(180,156)],2623,False),"ink-thin")
          + I(curve([(58,102),(136,102)],2624,False),"ink-thin")
          + I(curve([(58,154),(136,154)],2625,False),"ink-thin")), \
           A(poly([(x-8,y+8) for x,y in body],2626,bow=3))


def tire():
    """A car tire: deep ring, blocky tread bars."""
    def bar(a):
        t=a*math.pi/4
        return I(curve([(128+58*math.cos(t),128+58*math.sin(t)),
                        (128+90*math.cos(t),128+90*math.sin(t))],2627+a,False),"ink-thin")
    tread="".join(bar(a) for a in range(8))
    return (I(circ(128,128,104,2635))
          + I(circ(128,128,44,2636))
          + tread), \
           A(circ(120,136,104,2637,amt=6))


def trips():
    """A suitcase, section mark for travel. No other suitcase in the set."""
    body=[(36,82),(220,82),(220,214),(36,214)]
    return (I(poly(body,2638))
          + I(curve([(96,82),(98,50),(128,42),(158,50),(160,82)],2639,False))
          + I(curve([(36,150),(128,152),(220,150)],2640,False),"ink-thin")
          + I(poly([(110,138),(146,138),(146,164),(110,164)],2641))), \
           A(poly([(x-8,y+8) for x,y in body],2642,bow=3))


def trivia():
    """A question mark in a rounded badge."""
    return (I(circ(128,128,100,2643))
          + I(curve([(92,96),(102,66),(134,56),(166,74),(162,108),(132,128),(128,156)],
                    2644,False))
          + S(circ(128,190,11,2645,amt=1.4))), \
           A(circ(120,136,100,2646,amt=6))


def tv():
    """A flat-screen TV on a pedestal stand."""
    screen=[(26,48),(230,48),(230,172),(26,172)]
    return (I(poly(screen,2647))
          + I(poly([(110,172),(146,172),(146,202),(110,202)],2648,False))
          + I(curve([(66,214),(128,220),(190,214)],2649,False))), \
           A(poly([(x-8,y+8) for x,y in screen],2650,bow=3))


def vacuum():
    """A cordless stick vacuum: body, wand and floor head - all three or it's a lollipop."""
    body=[(84,50),(160,26),(186,96),(110,120)]
    return (I(poly(body,2651))
          + I(curve([(160,26),(196,16),(212,44)],2652,False))
          + I(curve([(136,116),(130,190)],2653,False))
          + I(poly([(46,190),(214,190),(200,232),(60,232)],2654))), \
           A(poly([(x-8,y+8) for x,y in body],2655,bow=3))


ICONS = [("style","Sneaker","fig",style),
         ("tag","Price tag","clay",tag),
         ("teak","Teak chair","kraft",teak),
         ("thermometer","Probe thermometer","cactus",thermometer),
         ("ticket","Ticket stub","manilla",ticket),
         ("tire","Tire","heather",tire),
         ("trips","Suitcase","kraft",trips),
         ("trivia","Trivia","accent",trivia),
         ("tv","Television","oat",tv),
         ("vacuum","Stick vacuum","cactus",vacuum)]
