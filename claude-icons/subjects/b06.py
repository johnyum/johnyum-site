import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from draw import SW, jit, curve, poly, circ, scribble, I, A, S, render


def map_pin():
    drop=[(128,26),(176,44),(196,90),(178,138),(128,226),(78,138),(60,90),(80,44)]
    return (I(curve(drop,2000))
          + I(circ(128,94,30,2001))), \
           A(curve([(x-8,y+8) for x,y in drop],2002,amt=4))


def masters():
    coat=[(128,92),(180,108),(202,160),(206,222),(162,232),(128,224),(94,232),(50,222),
          (54,160),(76,108)]
    return (I(curve(coat,2003))
          + I(curve([(128,92),(128,224)],2004,False))
          + I(curve([(96,100),(128,138),(160,100)],2005,False))
          + I(poly([(70,96),(128,62),(186,96)],2006,False))
          + I(curve([(128,62),(128,44),(142,36),(130,22),(112,28)],2007,False))), \
           A(curve([(x-8,y+8) for x,y in coat],2008,amt=4))


def milestone():
    steps=[(30,214),(30,168),(94,168),(94,124),(158,124),(158,80),(222,80),(222,214)]
    return (I(poly(steps,2009))
          + I(curve([(190,26),(200,46),(222,50),(206,66),(210,88),(190,78),
                     (170,88),(174,66),(158,50),(180,46)],2010,amt=2))), \
           A(poly([(x-8,y+8) for x,y in steps],2011,bow=3))


def mountain():
    ridge=[(20,210),(84,90),(118,144),(150,96),(236,210)]
    return (I(poly(ridge,2012))
          + I(curve([(58,134),(76,120),(94,138),(112,126)],2013,False),"ink-thin")), \
           A(poly([(x-8,y+8) for x,y in ridge],2015,bow=3))


def music():
    return (I(curve([(96,180),(96,52)],2016,False))
          + I(curve([(190,158),(190,32)],2017,False))
          + I(poly([(96,52),(190,32),(190,68),(96,88)],2018))
          + I(circ(70,186,28,2019))
          + I(circ(164,164,28,2020))), \
           A(poly([(88,60),(182,40),(182,76),(88,96)],2021,bow=3)
             + " " + circ(62,194,28,2022,amt=4))


def number():
    badge=[(44,40),(212,40),(212,216),(44,216)]
    return (I(poly(badge,2023))
          + I(curve([(86,84),(170,84)],2024,False))
          + I(curve([(170,84),(116,180)],2025,False))), \
           A(poly([(x-8,y+8) for x,y in badge],2026,bow=3))


def oven():
    body=[(34,44),(222,44),(222,222),(34,222)]
    return (I(poly(body,2027))
          + I(curve([(40,104),(128,106),(216,104)],2028,False))
          + I(poly([(70,140),(186,140),(186,196),(70,196)],2029))
          + I(circ(74,74,17,2030))
          + I(curve([(116,74),(196,74)],2031,False),"ink-thin")), \
           A(poly([(x-8,y+8) for x,y in body],2032,bow=3))


def paint():
    can=[(46,106),(186,106),(174,226),(58,226)]
    return (I(poly(can,2033))
          + I(curve([(46,106),(88,80),(146,82),(186,106)],2034,False))
          + I(poly([(138,110),(166,98),(224,30),(200,14)],2035))
          + I(curve([(152,104),(180,66)],2036,False),"ink-thin")
          + I(curve([(56,164),(178,164)],2037,False),"ink-thin")), \
           A(poly([(x-8,y+8) for x,y in can],2038,bow=3))


def palm_springs():
    house=[(56,160),(200,116),(200,224),(56,224)]
    return (I(circ(190,54,34,2039))
          + I(poly(house,2040))
          + I(poly([(30,170),(226,110)],2041,False))
          + I(poly([(84,180),(136,164),(136,206),(84,222)],2042),"ink-thin")), \
           A(poly([(x-8,y+8) for x,y in house],2043,bow=3))


def percent():
    badge=[(44,40),(212,40),(212,216),(44,216)]
    return (I(poly(badge,2050))
          + I(curve([(172,80),(84,176)],2051,False))
          + I(circ(92,92,22,2052))
          + I(circ(164,164,22,2053))), \
           A(poly([(x-8,y+8) for x,y in badge],2054,bow=3))


ICONS = [("map-pin","Map pin","clay",map_pin),
         ("masters","Masters jacket","olive",masters),
         ("milestone","Milestone","accent",milestone),
         ("mountain","Mountain","cactus",mountain),
         ("music","Music","heather",music),
         ("number","Number","manilla",number),
         ("oven","Oven","oat",oven),
         ("paint","Paint","fig",paint),
         ("palm-springs","Palm Springs","kraft",palm_springs),
         ("percent","Percent","clay",percent)]
