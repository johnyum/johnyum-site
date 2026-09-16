import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from draw import SW, jit, curve, poly, circ, scribble, I, A, S, render


def vent():
    slots = "".join(I(curve([(128 - w, y), (128, y + 2), (128 + w, y)], 2803 + i, False), "ink-thin")
                    for i, (y, w) in enumerate(((88, 66), (128, 78), (168, 66))))
    return (I(circ(128, 128, 94, 2801))
          + slots), \
           A(circ(120, 136, 94, 2802, amt=5))


def vr():
    body = [(28,84),(70,66),(186,66),(228,84),(232,148),(198,184),(150,180),(128,152),
            (106,180),(58,184),(24,148)]
    return (I(curve(body, 2810))
          + I(circ(80, 122, 28, 2811), "ink-thin")
          + I(circ(176, 122, 28, 2812), "ink-thin")
          + I(curve([(28,92),(10,82)], 2813, False))
          + I(curve([(228,92),(246,82)], 2814, False))), \
           A(curve([(x - 8, y + 8) for x, y in body], 2815, amt=4))


def water():
    drop = [(128,26),(158,74),(186,124),(180,170),(150,198),(128,204),(106,198),(76,170),
            (70,124),(98,74)]
    return (I(curve(drop, 2820))
          + I(curve([(56,228),(128,240),(200,228)], 2821, False), "ink-thin")), \
           A(curve([(x - 8, y + 8) for x, y in drop], 2822, amt=4))


def window():
    frame = [(48,36),(208,36),(208,184),(48,184)]
    return (I(poly(frame, 2830))
          + I(curve([(128,40),(128,180)], 2831, False), "ink-thin")
          + I(curve([(30,204),(128,212),(226,204)], 2832, False))), \
           A(poly([(x - 8, y + 8) for x, y in frame], 2833, bow=3))


def workouts():
    left  = [(38,66),(94,66),(94,190),(38,190)]
    right = [(162,66),(218,66),(218,190),(162,190)]
    return (I(poly(left, 2840, bow=1.8))
          + I(poly(right, 2841, bow=1.8))
          + I(curve([(94,128),(128,124),(162,128)], 2842, False))), \
           A(poly([(x - 8, y + 8) for x, y in left], 2843, bow=3))


def wrench():
    # wrench: ring end lower-left, open jaw upper-right
    jaw = [(210,62),(185,88),(155,60),(180,34)]
    return (I(circ(64, 190, 27, 2850))
          + I(curve([(80,172),(168,78)], 2851, False))
          + I(poly(jaw, 2852, False, bow=1.4))
          + I(poly([(216,196),(176,156),(156,176),(196,216)], 2853, bow=1.6))
          + I(curve([(168,166),(78,76)], 2854, False))), \
           A(circ(58, 198, 30, 2856, amt=5))


def yogurt():
    cup = [(78,84),(182,84),(170,200),(94,200)]
    return (I(poly(cup, 2860, bow=2.2))
          + I(curve([(84,110),(128,116),(176,110)], 2861, False), "ink-thin")
          + I(curve([(130,152),(188,56)], 2862, False))
          + I(circ(196, 42, 17, 2863))
          + I(circ(102, 76, 19, 2864))), \
           A(poly([(x - 8, y + 8) for x, y in cup], 2865, bow=3))


def youtube():
    badge = [(72,60),(184,60),(206,80),(206,176),(184,196),(72,196),(50,176),(50,80)]
    return (I(curve(badge, 2870))
          + I(poly([(108,92),(172,128),(108,164)], 2871, bow=1.6))), \
           A(curve([(x - 8, y + 8) for x, y in badge], 2872, amt=4))


ICONS = [("vent", "Vent", "heather", vent),
         ("vr", "VR", "cactus", vr),
         ("water", "Water", "cactus", water),
         ("window", "Window", "oat", window),
         ("workouts", "Workouts", "olive", workouts),
         ("wrench", "Wrench", "kraft", wrench),
         ("yogurt", "Yogurt", "manilla", yogurt),
         ("youtube", "YouTube", "clay", youtube)]
