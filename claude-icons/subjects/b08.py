import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from draw import SW, jit, curve, poly, circ, scribble, I, A, S, render


def scorecard():
    board=[(48,42),(208,42),(208,222),(48,222)]
    rows="".join(I(curve([(70,y),(186,y)],2404+i,False),"ink-thin")
                 for i,y in enumerate((112,150,188)))
    return (I(poly(board,2400))
          + I(poly([(100,28),(156,28),(156,60),(100,60)],2401,bow=1.6))
          + I(curve([(70,80),(186,80)],2402,False),"ink-thin")
          + I(curve([(128,74),(128,222)],2403,False),"ink-thin")
          + rows), \
           A(poly([(x-8,y+8) for x,y in board],2407,bow=3))


def sf_spots():
    left=[(78,222),(78,52)]
    deck=[(30,150),(128,158),(226,150)]
    return (I(poly([(78,226),(78,44),(60,44),(96,44)],2410,False,bow=1.6))
          + I(poly([(178,226),(178,44),(160,44),(196,44)],2411,False,bow=1.6))
          + I(curve(deck,2412,False))
          + I(curve([(78,60),(128,120),(178,60)],2413,False),"ink-thin")
          + I(curve([(30,96),(78,60)],2414,False),"ink-thin")
          + I(curve([(178,60),(226,96)],2415,False),"ink-thin")), \
           A(poly([(70,60),(186,60),(186,166),(70,166)],2416,bow=3))


def shield():
    sh=[(128,30),(206,58),(202,140),(128,226),(54,140),(50,58)]
    return (I(curve(sh,2420))
          + I(poly([(88,124),(118,156),(172,96)],2421,False,bow=1.6))), \
           A(curve([(x-8,y+8) for x,y in sh],2422,amt=4))


def shirt():
    body=[(38,124),(100,92),(128,114),(156,92),(218,124),(198,166),(178,156),(178,212),(78,212),(78,156),(58,166)]
    return (I(poly(body,2430,bow=1.8))
          + I(curve([(100,92),(128,126),(156,92)],2431,False),"ink-thin")
          + I(curve([(128,142),(128,204)],2432,False),"ink-thin")
          + I(poly([(38,124),(128,62),(218,124)],2436,False,bow=1.6),"ink-thin")
          + I(curve([(128,62),(128,44),(112,38),(124,26),(142,32)],2433,False))), \
           A(poly([(x-8,y+8) for x,y in body],2434,bow=3))


def shower():
    dome=[(58,104),(64,70),(96,46),(128,40),(160,46),(192,70),(198,104)]
    drops="".join(I(curve([(x,y),(x,y+40)],2444+i,False),"ink-thin")
                  for i,(x,y) in enumerate(((80,140),(128,156),(176,140))))
    return (I(curve(dome,2440,False))
          + I(curve([(52,106),(204,106)],2441,False))
          + I(curve([(128,40),(128,18)],2442,False))
          + I(curve([(128,18),(222,18),(222,56)],2443,False))
          + drops), \
           A(curve([(50,112),(56,78),(88,54),(120,48),(152,54),(184,78),(190,112)],2448,amt=4))


def shrimp():
    body=[(196,66),(214,110),(198,164),(150,198),(96,200),(60,174),(56,136),(84,112),(126,112),(150,132),(146,160),(116,166)]
    return (I(curve(body,2450,False))
          + I(curve([(196,66),(150,56),(108,42)],2451,False),"ink-thin")
          + I(curve([(196,66),(166,34),(138,16)],2452,False),"ink-thin")
          + I(circ(186,88,8,2453),"ink-thin")), \
           A(curve([(188,74),(206,118),(190,172),(142,206),(88,208),(52,182),(48,144),(76,120),(118,120),(142,140)],2454,amt=4))


def smoke():
    log=[(46,180),(72,158),(184,158),(212,180),(212,208),(184,228),(72,228),(46,208)]
    wisp=lambda x,s: I(curve([(x,148),(x-22,120),(x+18,92),(x-16,60),(x+8,34)],s,False),"ink-thin")
    return (I(poly(log,2460,bow=1.8))
          + I(curve([(72,158),(94,178),(94,208),(72,228)],2461,False),"ink-thin")
          + wisp(92,2462) + wisp(164,2463)), \
           A(curve([(x-8,y+8) for x,y in log],2464,amt=4))


def solar():
    panel=[(38,168),(96,64),(224,64),(166,168)]
    return (I(poly(panel,2470,bow=1.8))
          + I(poly([(67,116),(195,116)],2471,False,bow=1.6),"ink-thin")
          + I(poly([(128,64),(96,168)],2472,False,bow=1.6),"ink-thin")
          + I(poly([(190,64),(158,168)],2473,False,bow=1.6),"ink-thin")
          + I(curve([(102,168),(102,214)],2474,False))
          + I(curve([(64,220),(150,220)],2475,False))
          + I(circ(78,58,34,2476))), \
           A(poly([(x-8,y+8) for x,y in panel],2477,bow=3))


def sports():
    return (I(circ(128,128,88,2480))
          + I(curve([(128,40),(128,216)],2481,False),"ink-thin")
          + I(curve([(40,128),(216,128)],2482,False),"ink-thin")
          + I(curve([(62,66),(104,128),(62,190)],2483,False),"ink-thin")
          + I(curve([(194,66),(152,128),(194,190)],2484,False),"ink-thin")), \
           A(circ(118,138,88,2485,amt=5))


def steak():
    cut=[(72,58),(140,48),(178,70),(188,98),(214,114),(216,142),(188,158),(178,186),(136,208),(74,200),(36,158),(30,110),(44,74)]
    marks="".join(I(curve([(74+i*36,96),(62+i*36,166)],2491+i,False),"ink-thin")
                  for i in range(3))
    return (I(curve(cut,2490,t=0.9))
          + marks), \
           A(curve([(x-8,y+8) for x,y in cut],2495,amt=4))


ICONS=[("scorecard","Scorecard","oat",scorecard),
       ("sf-spots","SF spots","heather",sf_spots),
       ("shield","Shield","olive",shield),
       ("shirt","Shirt","cactus",shirt),
       ("shower","Shower","heather",shower),
       ("shrimp","Shrimp","clay",shrimp),
       ("smoke","Smoke","kraft",smoke),
       ("solar","Solar","manilla",solar),
       ("sports","Sports","accent",sports),
       ("steak","Steak","fig",steak)]
