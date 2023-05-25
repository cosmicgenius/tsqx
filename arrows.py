arrow_type = {
    "->": "EndArrow",
    "-->": "EndArrow",
    "<-": "BeginArrow",
    "<--": "BeginArrow",
    "<->": "Arrows",
    "->-": "MidArrow"
}

arrow_head = {
    "": "DefaultHead",
    "d": "DefaultHead",
    "s": "SimpleHead",
    "h": "HookHead",
    "t": "TeXHead",
}

def get_arrow_dict(arc, typ, head):
    arc_string = "a" if arc else ""
    arrow_val = (arrow_type[typ].replace("Arrow", "ArcArrow") \
                 if arc else arrow_type[typ], arrow_head[head])

    yield typ + head + arc_string, arrow_val
    if head != "" and arc_string != "":
        yield typ + arc_string + head, arrow_val

arrow_dict = { k : v \
               for arc in [True, False] \
               for typ in arrow_type \
               for head in arrow_head \
               for (k, v) in get_arrow_dict(arc, typ, head) }
