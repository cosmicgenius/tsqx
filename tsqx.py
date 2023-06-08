##########
## TSQX ##
##########

# original TSQ by evan chen

import re, sys
import parse
import arrows

def generate_points(kind, n):
    if kind == "triangle":
        return ["dir(110)", "dir(210)", "dir(330)"]
    elif kind == "regular":
        return [f"dir({(90 + i*360/n) % 360})" for i in range(n)]
    raise SyntaxError("Special command not recognized")

class Op:
    def emit(self):
        raise Exception("Operation not recognized")

    def post_emit(self):
        return None


class Blank(Op):
    def emit(self):
        return ""

class Point():
    def __init__(self, name, exp, **options):
        self.name = name
        self.exp = exp
        self.dot = options.get("dot", True)
        self.label = options.get("label", name)
        if self.label:
            for old, new in [
                ("'", "_prime"),
                ("{", "_lbrace_"),
                ("}", "_rbrace_"),
            ]:
                self.label = self.label.replace(new, old)
        self.direction = options.get("direction", f"dir({name})")

    def emit(self):
        return f"pair {self.name} = {self.exp};"

    def post_emit(self):
        args = [self.name]
        if self.label:
            args = [f'"${self.label}$"', *args, self.direction]
        if self.dot:
            return f"dot({', '.join(args)});"
        if len(args) > 1:
            return f"label({', '.join(args)});"


class Draw(Op):
    def __init__(self, exp, **options):
        self.exp = exp
        self.fill = options.get("fill", None)
        self.outline = options.get("outline", None)
        self.clip = options.get("clip", None)
        self.arrow = options.get("arrow", None) 

    def emit(self):
        arrow = f"{self.arrow[0]}({self.arrow[1]})" if self.arrow else None
        if self.fill:
            outline = self.outline or "defaultpen"
            return f"filldraw((path) {self.exp}, {self.fill}, {outline}" + \
                   f"{f', arrow={arrow}' if arrow else ''});"

        elif self.outline:
            return f"{'clipdraw' if self.clip else 'draw'}" + \
                   f"({self.exp}, {self.outline}" + \
                   f"{f', arrow={arrow}' if arrow else ''});"

        else:
            return f"{'clipdraw' if self.clip else 'draw'}({self.exp}" + \
                   f"{f', arrow={arrow}' if arrow else ''});"


class Parser:
    def __init__(self, **args):
        self.soft_label = args.get("soft_label", False)
        self.alias_map = {"": "dl", ":": "", ".": "d", ";": "l"}
        if self.soft_label:
            self.alias_map |= {"": "l", ";": "dl"}
        self.aliases = self.alias_map.keys() | self.alias_map.values()

    def sanitize(self, line):
        line = line.strip() + " "
        for old, new in [
            # ' not allowed in variable names
            ("'", "_prime"),
            ("{", "_lbrace_"),
            ("}", "_rbrace_"),
            # ~, =, / are separate tokens
            ("~", " ~ "),
            ("=", " = "),
            ("/", " / "),
        ]:
            line = line.replace(old, new)
        return line.strip()

    def parse_special(self, line, comment):
        if not line:
            raise SyntaxError("Can't parse special command")

        head, *tail = line.split()

        # put inline comment before
        if comment:
            yield Blank(), comment
            
        if head in ["triangle", "regular"]:
            for name, exp in zip(tail, generate_points(head, len(tail))):
                yield Point(name, exp), None
            return
        else:
            raise SyntaxError("Special command not recognized")

    def parse_name(self, line):
        if not line:
            raise SyntaxError("Can't parse point name")

        name, *rest = line.split()

        if rest and rest[-1] in self.aliases:
            *rest, opts = rest
        else:
            opts = ""
        opts = self.alias_map.get(opts, opts)
        options = {"dot": "d" in opts, "label": "l" in opts and name}

        if rest:
            dirs, *rest = rest
            if dir_pairs := re.findall(r"(\d+)([A-Z]+)", dirs):
                options["direction"] = "+".join(f"{n}*plain.{w}" for n, w in dir_pairs)
            elif dirs.isdigit():
                options["direction"] = f"dir({dirs})"
            elif re.fullmatch(r"N?S?E?W?", dirs):
                options["direction"] = f"plain.{dirs}"
            else:
                rest.append(dirs)
        if "direction" not in options:
            options["direction"] = f"dir({name})"

        if rest:
            raise SyntaxError("Can't parse point name")
        return name, options

    def parse_draw(self, line):
        try:
            idx = line.index("/")
            fill_ = line[:idx].split()
            outline_ = line[idx + 1:].split()
        except ValueError:
            fill_ = []
            outline_ = line.split()

        fill = []
        for pen in fill_:
            if re.fullmatch(r"\d*\.?\d*", pen): # decimal for opacity
                fill.append(f"opacity({pen})")
            else:
                fill.append(pen)
        
        outline = []
        clip = False
        arrow = None
        for pen in outline_:
            if pen == 'x': # clipdraw
                clip = True
            elif pen in arrows.arrow_dict: # arrow 
                arrow = arrows.arrow_dict[pen]
            elif re.fullmatch(r"\d*\.?\d*", pen): # decimal for linewidth
                outline.append(f"linewidth({pen})")
            else:
                outline.append(pen)

        return { 
            "fill": "+".join(fill),
            "outline": "+".join(outline),
            "clip": clip,
            "arrow": arrow
        }

    def parse(self, line):
        line, *comment = line.split("#", 1)
        line = self.sanitize(line)

        if line.strip() == "":
            yield (Blank(), comment)
            return
        # special
        if line[0] == '~':
            yield from self.parse_special(line[1:], comment)
            return
        # point
        try:
            idx = line.index("=")
            name, options = self.parse_name(line[:idx])
            exp = parse.SyntaxNode(line[idx + 1:]).emit()

            yield Point(name, exp, **options), comment
            return
        except ValueError:
            pass
        # draw with options
        try:
            idx = line.index("/")
            exp = parse.SyntaxNode(line[:idx]).emit()

            options = self.parse_draw(line[idx + 1 :])
            yield Draw(exp, **options), comment
            return
        except ValueError:
            pass
        # draw without options
        exp = parse.SyntaxNode(line).emit()
        yield Draw(exp), comment
        return


class Emitter:
    def __init__(self, lines, print_=print, **args):
        self.lines = lines
        self.print = print_
        self.preamble = args.get("preamble", False)
        self.size = args.get("size", "8cm")
        self.parser = Parser(**args)

    def emit(self):
        # kind of required?
        self.print("import geometry;")
        if self.preamble:
            #self.print("import olympiad;")
            #self.print("import cse5;")
            self.print("size(%s);" % self.size)
            self.print("defaultpen(fontsize(9pt));")
            self.print('settings.outformat="pdf";')

        ops = [oc for line in self.lines for oc in self.parser.parse(line)]
        for op, comment in ops:
            out = op.emit()
            if comment:
                out = f"{out} //{comment[0]}".strip()
            self.print(out)
        self.print()
        for op, comment in ops:
            if out := op.post_emit():
                self.print(out)


def main():
    from argparse import ArgumentParser

    argparser = ArgumentParser(description="Generate Asymptote code.")
    argparser.add_argument(
        "-p",
        "--pre",
        help="Adds a preamble.",
        action="store_true",
        dest="preamble",
        default=False,
    )
    argparser.add_argument(
        "fname",
        help="Read from file rather than stdin.",
        metavar="filename",
        nargs="?",
        default="",
    )
    argparser.add_argument(
        "-s",
        "--size",
        help="Set image size in preamble.",
        action="store",
        dest="size",
        default="8cm",
    )
    argparser.add_argument(
        "-sl",
        "--soft-label",
        help="Don't draw dots on points by default.",
        action="store_true",
        dest="soft_label",
        default=False,
    )
    args = argparser.parse_args()
    stream = open(args.fname, "r") if args.fname else sys.stdin
    emitter = Emitter(stream, print, **vars(args))
    emitter.emit()


if __name__ == "__main__":
    main()
