import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from draw import SW, jit, curve, poly, circ, scribble, I, A, S, render


def cooking():
    pan=[(108,106),(158,116),(182,150),(158,186),(108,196),(58,186),(34,150),(58,116)]
    return (I(curve(pan,1401))
          + I(curve([(178,136),(210,110),(236,86)],1402,False))
          + I(curve([(70,132),(108,124),(148,132)],1403,False),"ink-thin")), \
           A(curve([(x-8,y+8) for x,y in pan],1404,amt=4))


def corn():
    ear=[(128,38),(160,76),(166,134),(148,180),(128,198),(108,180),(90,134),(96,76)]
    husk=(I(curve([(114,196),(68,148),(38,56),(86,112),(112,164)],1406))
        + I(curve([(142,196),(188,148),(218,56),(170,112),(144,164)],1407)))
    return (I(curve(ear,1405))
          + husk
          + I(curve([(94,78),(128,86),(162,78)],1408,False),"ink-thin")
          + I(curve([(88,122),(128,130),(168,122)],1409,False),"ink-thin")
          + I(curve([(128,58),(128,166)],1446,False),"ink-thin")), \
           A(curve([(x-8,y+8) for x,y in ear],1410,amt=4))


def crib():
    slats="".join(I(curve([(x,72),(x,188)],1412+i,False),"ink-thin")
                  for i,x in enumerate((80,112,144,176)))
    return (I(curve([(48,46),(48,224)],1411,False))
          + I(curve([(208,46),(208,224)],1417,False))
          + I(curve([(48,70),(128,64),(208,70)],1418,False))
          + I(curve([(48,186),(128,192),(208,186)],1447,False))
          + slats), \
           A(poly([(x-8,y+8) for x,y in
                   [(50,66),(206,66),(206,190),(50,190)]],1419,bow=3))


def cursor():
    arrow=[(58,30),(58,192),(100,152),(126,216),(156,202),(130,140),(184,136)]
    return I(poly(arrow,1420,bow=1.8)), A(poly([(x-8,y+8) for x,y in arrow],1421,bow=2.4))


def curtains():
    win=[(46,36),(210,36),(210,206),(46,206)]
    drape=[(50,40),(106,50),(88,110),(104,166),(52,202)]
    return (I(poly(win,1422))
          + I(curve(drape,1423))
          + I(curve([(34,222),(128,230),(222,222)],1424,False),"ink-thin")), \
           A(curve([(x-8,y+8) for x,y in drape],1425,amt=4))


def design():
    nib=[(88,34),(168,34),(180,118),(128,226),(76,118)]
    return (I(poly(nib,1426,bow=2.0))
          + I(circ(128,100,16,1427),"ink-thin")
          + I(curve([(128,142),(128,212)],1428,False),"ink-thin")), \
           A(curve([(x-8,y+8) for x,y in nib],1429,amt=4))


def diaper():
    body=[(44,60),(128,50),(212,60),(206,98),(176,130),(162,182),(128,162),(94,182),
          (80,130),(50,98)]
    return (I(curve(body,1430,t=0.8))
          + I(curve([(56,92),(128,100),(200,92)],1431,False),"ink-thin")), \
           A(curve([(x-8,y+8) for x,y in body],1432,amt=4))


def drill():
    sil=[(40,70),(148,70),(148,98),(198,98),(198,134),(148,134),(148,142),
         (120,142),(120,216),(70,216),(70,142),(40,142)]
    return (I(poly(sil,1433,bow=1.8))
          + I(curve([(200,116),(236,116)],1434,False))), \
           A(poly([(x-8,y+8) for x,y in sil],1435,bow=2.6))


def entertainment():
    box=[(70,100),(186,100),(170,214),(86,214)]
    return (I(poly(box,1436,bow=2.0))
          + I(curve([(128,104),(128,210)],1437,False),"ink-thin")
          + I(circ(94,82,22,1438))
          + I(circ(128,62,24,1439))
          + I(circ(164,82,22,1440))), \
           A(poly([(x-8,y+8) for x,y in box],1441,bow=3))


def everything_else():
    return (I(curve([(128,44),(128,212)],1442,False))
          + I(curve([(55,86),(201,170)],1443,False))
          + I(curve([(201,86),(55,170)],1444,False))), \
           A(circ(118,138,62,1445,amt=5))


ICONS=[("cooking","Cooking","clay",cooking),
       ("corn","Corn","manilla",corn),
       ("crib","Crib","cactus",crib),
       ("cursor","Cursor","heather",cursor),
       ("curtains","Curtains","fig",curtains),
       ("design","Design","accent",design),
       ("diaper","Diaper","oat",diaper),
       ("drill","Drill","kraft",drill),
       ("entertainment","Entertainment","olive",entertainment),
       ("everything-else","Everything else","clay",everything_else)]
