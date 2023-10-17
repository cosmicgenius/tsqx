# some abbreviations

# geometry.asy's excenter(A, B, C) is tangent to AB (!) 
# this excenter is tangent to BC (like a normal person would do)
def excenter(A, B, C):
    return f"excenter({B}, {C}, {A})"

def excircle(A, B, C):
    return f"excircle({B}, {C}, {A})"

def orthocenter(A, B, C):
    return f"orthocentercenter({A}, {B}, {C})"

# first intersection point
def IP(p, q, n=0):
    return f"intersectionpoints({p}, {q})[{n}]"

# "other" intersection point (i.e. second)
def OP(p, q):
    return f"intersectionpoints({p}, {q})[1]"

def foot(P, A, B):
    return f"foot(triangle({A}, {B}, {P}).VC)"

# finds the centroid of a list of points
def centroid(*pts):
    return f"(({' + '.join(pts)}) / {len(pts)})"

def dist(A, B):
    return f"abs({A} - {B})"

# vector argument
def varg(A, B):
    return f"unit({A} - {B})"

# circle through a point
def CP(O, P):
    return f"circle({O}, abs({O} - {P}))"

# circle with a particular radius
def CR(O, r):
    return f"circle({O}, {r})"

# vertex "A" of a particular geometry,asy triangle
def VA(t):
    return f"{t}.VA"

def VB(t):
    return f"{t}.VB"

def VC(t):
    return f"{t}.VC"
