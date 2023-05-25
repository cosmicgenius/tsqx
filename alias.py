# some abbreviations

# geometry.asy's excenter(A, B, C) is tangent to AB (!) 
# this excenter is tangent to BC (like a normal person would do)
def excenter(A, B, C):
    return f"excenter({B}, {C}, {A})"

def orthocenter(A, B, C):
    return f"orthocentercenter({A}, {B}, {C})"

def IP(p, q, n=0):
    return f"intersectionpoints({p}, {q})[{n}]"

def OP(p, q):
    return f"intersectionpoints({p}, {q})[1]"

def foot(P, A, B):
    return f"foot(triangle({A}, {B}, {P}).VC)"

def centroid(A, B, C):
    return f"(({A} + {B} + {C}) / 3)"

def CP(O, P):
    return f"circle({O}, distance({O}, {P}))"

def CR(O, r):
    return f"circle({O}, {r})"

def VA(t):
    return f"{t}.VA"

def VA(t):
    return f"{t}.VB"

def VA(t):
    return f"{t}.VC"

def circle(A, B, C):
    return f"circumcircle({A}, {B}, {C})"
