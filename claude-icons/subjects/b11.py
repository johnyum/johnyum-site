import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from draw import SW, jit, curve, poly, circ, scribble, I, A, S, render


def tech():
    head=[(88,52),(168,52),(168,120),(88,120)]
    return (I(curve([(110,18),(110,52)],3200,False))
          + I(curve([(146,18),(146,52)],3201,False))
          + I(poly(head,3202))
          + I(curve([(128,120),(128,152),(80,176),(94,212),(158,228),(200,198)],3203,False))), \
           A(poly([(x-8,y+8) for x,y in head],3204,bow=3))


ICONS = [("tech","Tech","heather",tech)]
