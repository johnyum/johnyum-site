import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from draw import SW, jit, curve, poly, circ, scribble, I, A, S, render


def ac():
    body=[(30,62),(226,62),(226,126),(30,126)]
    return (I(poly(body,1000))
          + I(curve([(46,110),(128,112),(210,110)],1001,False),"ink-thin")
          + I(curve([(66,164),(94,150),(122,164),(150,150),(178,164)],1002,False))
          + I(curve([(66,204),(94,190),(122,204),(150,190),(178,204)],1003,False))), \
           A(poly([(x-8,y+8) for x,y in body],1004,bow=3))


def baby():
    ball=(112,86,48)
    return (I(circ(*ball,1005))
          + I(curve([(112,136),(122,182),(128,206)],1006,False))
          + I(circ(130,222,16,1007))), \
           A(circ(104,94,48,1008,amt=4))


def bank():
    ped=[(128,30),(232,86),(24,86)]
    cols="".join(I(curve([(x,104),(x,184)],1009+i,False)) for i,x in enumerate((68,128,188)))
    return (I(poly(ped,1012))
          + I(curve([(30,104),(128,102),(226,104)],1013,False))
          + cols
          + I(curve([(30,198),(128,200),(226,198)],1014,False))
          + I(curve([(18,224),(128,226),(238,224)],1015,False))), \
           A(poly([(x-8,y+8) for x,y in ped],1016,bow=3))


def barbell():
    L=[(50,76),(86,76),(86,180),(50,180)]
    R=[(170,76),(206,76),(206,180),(170,180)]
    return (I(curve([(26,128),(128,130),(230,128)],1017,False))
          + I(poly(L,1018)) + I(poly(R,1019))), \
           A(poly([(x-8,y+8) for x,y in L],1020,bow=3)
             + " " + poly([(x-8,y+8) for x,y in R],1021,bow=3))


def bottle():
    body=[(94,70),(162,70),(172,112),(172,212),(150,232),(106,232),(84,212),(84,112)]
    return (I(curve([(110,20),(128,12),(146,20),(150,46),(106,46)],1022))
          + I(poly([(96,46),(160,46),(160,70),(96,70)],1023))
          + I(curve(body,1024))
          + I(curve([(104,130),(136,130)],1025,False),"ink-thin")
          + I(curve([(104,166),(136,166)],1026,False),"ink-thin")), \
           A(curve([(x-8,y+8) for x,y in body],1027,amt=4))


def broccoli():
    crown=[(128,26),(154,44),(180,32),(196,60),(214,86),(196,116),(198,144),(160,150),
           (128,142),(96,150),(58,144),(60,116),(42,86),(60,60),(76,32),(102,44)]
    return (I(curve(crown,1028,t=0.8))
          + I(curve([(128,58),(126,116)],1029,False),"ink-thin")
          + I(curve([(86,82),(106,124)],1030,False),"ink-thin")
          + I(curve([(172,82),(152,124)],1031,False),"ink-thin")
          + I(poly([(104,146),(102,214),(152,214),(150,146)],1032,False))), \
           A(curve([(x-8,y+8) for x,y in crown],1033,amt=4))


def bug():
    body=[(128,72),(170,86),(184,126),(174,174),(128,198),(82,174),(72,126),(86,86)]
    legs="".join(I(curve(p,1034+i,False)) for i,p in enumerate([
        [(80,102),(38,84)],[(72,134),(28,134)],[(82,168),(44,194)],
        [(176,102),(218,84)],[(184,134),(228,134)],[(174,168),(212,194)]]))
    return (I(curve(body,1040))
          + I(circ(128,54,22,1041))
          + I(curve([(114,38),(94,16)],1042,False))
          + I(curve([(142,38),(162,16)],1043,False))
          + legs
          + I(curve([(128,84),(128,190)],1044,False),"ink-thin")), \
           A(curve([(x-8,y+8) for x,y in body],1045,amt=4))


def bulb():
    glass=[(128,20),(172,36),(190,78),(174,118),(154,140),(152,158),(104,158),(102,140),
           (82,118),(66,78),(84,36)]
    return (I(curve(glass,1046))
          + I(poly([(108,158),(148,158),(146,208),(110,208)],1047))
          + I(curve([(110,183),(146,183)],1048,False),"ink-thin")), \
           A(curve([(x-8,y+8) for x,y in glass],1049,amt=4))


def calculator():
    body=[(56,20),(200,20),(200,236),(56,236)]
    keys="".join(I(circ(x,y,14,1050+i)) for i,(x,y) in enumerate(
        [(96,128),(160,128),(96,184),(160,184)]))
    return (I(poly(body,1054))
          + I(poly([(78,44),(178,44),(178,86),(78,86)],1055))
          + keys), \
           A(poly([(x-8,y+8) for x,y in body],1056,bow=3))


def calendar():
    page=[(32,50),(224,50),(224,224),(32,224)]
    sq="".join(I(poly([(x,y),(x+34,y),(x+34,y+34),(x,y+34)],1057+i),"ink-thin")
               for i,(x,y) in enumerate([(70,122),(152,122),(70,176),(152,176)]))
    return (I(poly(page,1061))
          + I(curve([(38,94),(128,96),(218,94)],1062,False))
          + I(curve([(82,50),(82,22)],1063,False))
          + I(curve([(174,50),(174,22)],1064,False))
          + sq), \
           A(poly([(x-8,y+8) for x,y in page],1065,bow=3))


ICONS = [("ac","Air conditioner","cactus",ac),
         ("baby","Baby rattle","fig",baby),
         ("bank","Bank","oat",bank),
         ("barbell","Barbell","accent",barbell),
         ("bottle","Baby bottle","manilla",bottle),
         ("broccoli","Broccoli","olive",broccoli),
         ("bug","Bug","kraft",bug),
         ("bulb","Light bulb","manilla",bulb),
         ("calculator","Calculator","heather",calculator),
         ("calendar","Calendar","clay",calendar)]
