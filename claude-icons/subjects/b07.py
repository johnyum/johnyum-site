import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from draw import SW, jit, curve, poly, circ, scribble, I, A, S, render


def phone():
    base=[(40,132),(216,132),(230,224),(26,224)]
    hand=[(44,70),(80,54),(176,54),(212,70),(212,94),(176,80),(80,80),(44,94)]
    return (I(poly(base,2200))
          + I(circ(128,178,26,2201))
          + S(circ(128,178,6,2202,amt=1.2))
          + I(curve([(84,132),(84,90)],2203,False))
          + I(curve([(172,132),(172,90)],2204,False))
          + I(curve(hand,2205))), \
           A(poly([(x-8,y+8) for x,y in base],2206,bow=3))


def photo():
    frame=[(36,30),(220,30),(220,226),(36,226)]
    return (I(poly(frame,2210))
          + I(curve([(42,178),(128,180),(214,178)],2211,False))
          + I(curve([(56,156),(92,104),(124,156)],2212,False),"ink-thin")
          + I(curve([(110,156),(150,92),(198,156)],2213,False),"ink-thin")
          + I(circ(178,72,16,2214),"ink-thin")), \
           A(poly([(x-8,y+8) for x,y in frame],2215,bow=3))


def podcast():
    cap=[(96,26),(160,26),(160,124),(96,124)]
    return (I(curve([(96,58),(94,94),(96,124),(128,140),(160,124),(162,94),(160,58),(128,42)],2220))
          + I(curve([(60,112),(64,152),(128,180),(192,152),(196,112)],2221,False))
          + I(curve([(128,180),(128,226)],2222,False))
          + I(curve([(84,226),(128,232),(172,226)],2223,False))
          + I(curve([(30,64),(16,104),(30,146)],2224,False),"ink-thin")
          + I(curve([(226,64),(240,104),(226,146)],2225,False),"ink-thin")), \
           A(curve([(88,50),(86,94),(88,126),(120,144),(152,126),(154,94),(152,50),(120,36)],2226,amt=4))


def pool():
    basin=[(24,104),(150,66),(236,104),(112,152)]
    return (I(poly(basin,2230))
          + I(poly([(24,104),(24,148),(112,196),(112,152)],2231,False))
          + I(poly([(236,104),(236,146),(112,196)],2232,False))
          + I(curve([(60,120),(94,108),(128,124),(162,110)],2233,False),"ink-thin")
          + I(curve([(92,150),(126,138),(160,154),(194,140)],2234,False),"ink-thin")
          + I(curve([(172,32),(172,92)],2235,False))
          + I(curve([(212,20),(212,80)],2236,False))
          + I(curve([(172,44),(212,32)],2237,False),"ink-thin")
          + I(curve([(172,72),(212,60)],2239,False),"ink-thin")), \
           A(poly([(x-8,y+8) for x,y in basin],2238,bow=3))


def razor():
    head=[(44,44),(212,44),(212,92),(44,92)]
    body=[(84,92),(172,92),(158,224),(98,224)]
    teeth="".join(I(curve([(x,42),(x,16)],2245+i,False),"ink-thin")
                  for i,x in enumerate((80,128,176)))
    return (I(poly(head,2240))
          + teeth
          + I(poly(body,2242))
          + I(circ(128,152,16,2243),"ink-thin")), \
           A(poly([(x-8,y+8) for x,y in body],2244,bow=3))


def refi():
    house=[(128,92),(180,128),(180,184),(76,184),(76,128)]
    return (I(poly(house,2250))
          + I(poly([(108,184),(108,146),(148,146),(148,184)],2251,False),"ink-thin")
          + I(curve([(40,168),(22,110),(64,52),(130,36)],2252,False))
          + I(poly([(112,18),(140,38),(108,54)],2253))
          + I(curve([(216,88),(234,146),(192,204),(126,220)],2254,False))
          + I(poly([(144,238),(116,218),(148,202)],2255))), \
           A(poly([(x-8,y+8) for x,y in house],2256,bow=3))


def restaurant():
    plate=(128,132,56)
    return (I(circ(*plate,2260))
          + I(circ(128,132,30,2261),"ink-thin")
          + I(poly([(16,34),(40,46),(40,116),(16,116)],2262))
          + I(curve([(28,116),(28,226)],2263,False))
          + I(curve([(226,36),(226,96),(210,110),(226,226)],2264,False))
          + I(curve([(206,36),(206,90)],2265,False),"ink-thin")
          + I(curve([(246,36),(246,90)],2266,False),"ink-thin")), \
           A(circ(120,140,56,2267,amt=5))


def rice_bowl():
    bowl=[(32,116),(224,116),(196,206),(60,206)]
    return (I(poly(bowl,2270))
          + I(curve([(56,116),(78,100),(128,90),(178,102),(200,116)],2271,False))
          + I(curve([(24,116),(128,110),(232,116)],2273,False))
          + I(curve([(20,56),(238,32)],2274,False))
          + I(curve([(22,82),(240,58)],2275,False))), \
           A(poly([(x-8,y+8) for x,y in bowl],2276,bow=3))


def running():
    shoe=[(26,200),(28,168),(58,156),(94,148),(120,124),(154,112),(188,110),(204,136),
          (212,168),(226,180),(230,200)]
    return (I(curve(shoe,2280))
          + I(curve([(30,176),(128,182),(226,176)],2281,False),"ink-thin")
          + I(curve([(112,142),(136,162)],2282,False),"ink-thin")
          + I(curve([(140,128),(164,150)],2283,False),"ink-thin")
          + I(curve([(12,52),(96,48)],2284,False))
          + I(curve([(38,88),(122,84)],2285,False))), \
           A(curve([(x-8,y+8) for x,y in shoe],2286,amt=4))


def scales():
    return (I(curve([(128,40),(128,208)],2290,False))
          + I(curve([(30,64),(128,52),(226,64)],2291,False))
          + I(circ(128,34,14,2292),"ink-thin")
          + I(curve([(34,66),(34,100)],2293,False),"ink-thin")
          + I(curve([(222,66),(222,100)],2294,False),"ink-thin")
          + I(curve([(2,100),(34,142),(68,100)],2295,False))
          + I(curve([(190,100),(222,142),(254,100)],2296,False))
          + I(curve([(78,222),(128,214),(178,222)],2297,False))), \
           A(curve([(0,108),(28,150),(62,108)],2298,amt=4))


ICONS = [("phone","Rotary phone","heather",phone),
         ("photo","Photo print","cactus",photo),
         ("podcast","Podcast mic","kraft",podcast),
         ("pool","Swimming pool","cactus",pool),
         ("razor","Electric razor","oat",razor),
         ("refi","Refinance","olive",refi),
         ("restaurant","Restaurant","manilla",restaurant),
         ("rice-bowl","Rice bowl","clay",rice_bowl),
         ("running","Running shoe","accent",running),
         ("scales","Scales","fig",scales)]
