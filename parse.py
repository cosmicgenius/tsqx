# we want
#
# dir 110 => dir(110)
# incenter A B C => incenter(A, B, C)
# / (+ A B) 2 => (A + B) / 2
# / (+ A B C D) 4 => (A + B + C + D) / 4
# - (* 2 A) B => 2 * A - B
# (rotate -30 E (extension A (foot A B C) C E)) => rotate(-30, E) * extension(A, foot(A, B, C), C, E);
# + O (rotate 90 (- P O)) => O + rotate(90) * (P - O)
# (shift (0, 1) (rotate -30 E (foot A B C))) => shift((0, 1)) * rotate(-30, E) * foot(A, B, C)

import re
import alias

function_name = re.compile(r'^[a-zA-Z][a-zA-Z0-9]*$')
transforms = ["identity", "shift", "xscale", "yscale", "scale", \
              "slant", "rotate", "reflect", "zeroTransform", \
              "inversion"]
# inversion is a geometry.asy special case?

# abstract syntax tree node
class SyntaxNode:
    def __init__(self, exp): # args in the future
        self.raw_text = ""
        self.children = []

        # pad spaces
        exp = exp.replace(')', " ) ")
        exp = exp.replace('(', " ( ")
        exp = ' '.join(exp.split()) # collapse multiple spaces into one

        # respect commas
        exp = exp.replace(", ", ',')
        exp = exp.replace(" ,", ',')

        exp = exp.strip()
        while exp[0] == '(' and exp[-1] == ')':
            exp = exp[1:-1]
            exp = exp.strip()

        # leaf
        if ' ' not in exp.strip():
            self.raw_text = exp.strip()
            return

        exp = exp + ' '

        # custom tokenize respecting parentheses
        depth = 0 # parentheses depth
        cur_token = ""

        # extra space to force end of last child expression
        for char in exp:
            if char == '(':
                depth += 1
                # do not save the beginning '(' of a child expression
                if depth != 1:
                    cur_token += char
            elif char == ')':
                depth -= 1
                # do not save the end ')' of a child expression
                if depth != 0:
                    cur_token += char
            else:
                # ends child expression on space
                if depth == 0 and char == ' ':
                    self.children.append(SyntaxNode(cur_token))
                    cur_token = ""
                else:
                    cur_token += char

        if depth != 0:
            raise ValueError("Mismatched parentheses in expression")

    # compile and emit text
    def emit(self):
        if self.raw_text != "":
            # if it's a tuple
            if ',' in self.raw_text:
                return f"({self.raw_text})"

            return self.raw_text

        if len(self.children) == 1:
            return f"({self.children[0].emit()})"

        token0 = self.children[0].emit()
        true_children = [child.emit() for child in self.children[1:]]
        
        if function_name.match(token0):
            # transform like rotate
            if token0 in transforms:
                return f"{token0}({', '.join(true_children[:-1])}) * {true_children[-1]}"

            if token0 in dir(alias) and token0[0] != '_':
                return getattr(alias, token0) (*true_children)

            # function like incenter
            return f"{token0}({', '.join(true_children)})"

        # operator like +
        else:
            return f"({f' {token0} '.join(true_children)})"

#assert(parse_ast("z (a b) (d) e f (g PPP ( h (i + j )))") 
#       == [['z'], ['a b'], ['d'], ['e'], ['f'], [['g'], ['PPP'], [['h'], ['i + j']]]])

def test():
    assert(SyntaxNode("(a )").emit() == \
                      "a")
    assert(SyntaxNode("+ A B C D").emit() == \
                      "(A + B + C + D)")
    assert(SyntaxNode("+ (+ A B) (+ A B)").emit() == \
                      "((A + B) + (A + B))")
    assert(SyntaxNode("+ (* 2 A) (* 2 B)").emit() == \
                      "((2 * A) + (2 * B))")
    assert(SyntaxNode("(1, 2)").emit() == \
                      "(1,2)")
    assert(SyntaxNode("dir 110").emit() == \
                      "dir(110)")
    assert(SyntaxNode("+ (1, 2) (3, 4)").emit() == \
                      "((1,2) + (3,4))")
    assert(SyntaxNode("/ (+ A B C D) 4").emit() == \
                      "((A + B + C + D) / 4)")
    assert(SyntaxNode("- (* 2 A) B").emit() == \
                      "((2 * A) - B)")
    assert(SyntaxNode("z (a b)(d ) e (f g ( h (+ i j) )) ").emit() == \
                      "z(a(b), d, e, f(g, h((i + j))))")
    assert(SyntaxNode("+ O (rotate 90 (- P O))").emit() == \
                      "(O + rotate(90) * (P - O))")
    assert(SyntaxNode("(scale 2 (extension A (foot A B C) C E))").emit() == \
                      "scale(2) * extension(A, foot(A, B, C), C, E)")

if __name__ == "__main__":
    test()
