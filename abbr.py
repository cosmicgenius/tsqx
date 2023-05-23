# some abbreviations

# from https://github.com/vEnhance/dotfiles/blob/main/py-scripts/tsq.py
short_names = {
    "circle": "circumcircle",
    "rightangle": "rightanglemark",
}

def excenter(A, B, C):
    return f"2 * circumcenter(incenter({A}, {B}, {C}), {B}, {C}) - incenter({A}, {B}, {C})"

def distance(P, Q):
    return f"abs(P - Q)"

functions = {
    "excenter": excenter,
    "dist": distance,
}

