import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from draw import SW, jit, curve, poly, circ, scribble, I, A, S, render

OFF = lambda pts, dx=-8, dy=8: [(x+dx, y+dy) for x, y in pts]


def paper():
    """A plain sheet, two ruled lines. Sits at 16pt, so nothing else earns a place."""
    sheet=[(64,30),(192,30),(192,226),(64,226)]
    return (I(poly(sheet,3300,bow=2.6))
          + I(curve([(92,96),(166,96)],3301,False),"ink-thin")
          + I(curve([(92,148),(144,148)],3302,False),"ink-thin")), \
           A(poly(OFF(sheet),3303,bow=3))


ICONS = [("paper","Paper","cactus",paper)]
