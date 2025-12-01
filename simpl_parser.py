import re
from simpl_ast import *


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.tokens = self.tokenize()
        self.idx = 0

    def tokenize(self):
        keywords = {'let', 'in', 'end', 'if', 'then',
                    'else', 'while', 'do', 'fn', 'rec'}

        token_specs = [
            ('COMMENT', r'\(\*.*?\*\)'),
            ('NUM', r'\d+'),
            ('ID', r'[a-zA-Z_][a-zA-Z0-9_\']*'),
            ('SYMBOLS', r':=|::|<=|>=|<>|=>|->|[-+*/%~=<>!;,()]'),
            ('SKIP', r'[ \t\r\n]+'),
            ('MISC', r'.'),
        ]
        tokens = []
        i = 0
        while i < len(self.text):
            if self.text[i:i+2] == '(*':
                depth = 1
                i += 2
                while i < len(self.text) and depth > 0:
                    if self.text[i:i+2] == '(*':
                        depth += 1
                        i += 2
                    elif self.text[i:i+2] == '*)':
                        depth -= 1
                        i += 2
                    else:
                        i += 1
                continue

            match = None
            for type, regex in token_specs:
                if type == 'COMMENT':
                    continue
                regex_compiled = re.compile(regex)
                m = regex_compiled.match(self.text, i)
                if m:
                    match = m
                    val = m.group(0)
                    if type == 'ID' and val in keywords:
                        tokens.append(('KEYWORD', val))
                    elif type != 'SKIP':
                        tokens.append((type, val))
                    i = m.end()
                    break
            if not match:
                i += 1
        return tokens

    def peek(self):
        if self.idx < len(self.tokens):
            return self.tokens[self.idx]
        return ('EOF', None)

    def consume(self, type=None, val=None):
        t = self.peek()
        if type and t[0] != type:
            return None
        if val and t[1] != val:
            return None
        self.idx += 1
        return t


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer

    def parse(self):
        return self.expr()

    def expr(self):
        return self.parse_let()

    def parse_let(self):
        t = self.lexer.peek()
        if t[1] == 'let':
            self.lexer.consume()
            name = self.lexer.consume('ID')[1]
            self.lexer.consume(val='=')
            e1 = self.expr()
            self.lexer.consume(val='in')
            e2 = self.expr()
            self.lexer.consume(val='end')
            return Let(name, e1, e2)
        return self.parse_cond()

    def parse_cond(self):
        t = self.lexer.peek()
        if t[1] == 'if':
            self.lexer.consume()
            e1 = self.expr()
            self.lexer.consume(val='then')
            e2 = self.expr()
            self.lexer.consume(val='else')
            e3 = self.expr()
            return Cond(e1, e2, e3)
        if t[1] == 'while':
            self.lexer.consume()
            e1 = self.expr()
            self.lexer.consume(val='do')
            e2 = self.expr()
            return Loop(e1, e2)
        return self.parse_fn()

    def parse_fn(self):
        t = self.lexer.peek()
        if t[1] == 'fn':
            self.lexer.consume()
            x = self.lexer.consume('ID')[1]
            self.lexer.consume(val='=>')
            e = self.expr()
            return Fn(x, e)
        if t[1] == 'rec':
            self.lexer.consume()
            x = self.lexer.consume('ID')[1]
            self.lexer.consume(val='=>')
            e = self.expr()
            return Rec(x, e)
        return self.parse_seq()

    def parse_seq(self):
        left = self.parse_assign()
        while self.lexer.peek()[1] == ';':
            self.lexer.consume()
            right = self.parse_assign()
            left = Seq(left, right)
        return left

    def parse_assign(self):
        left = self.parse_orelse()
        while self.lexer.peek()[1] == ':=':
            self.lexer.consume()
            right = self.parse_orelse()
            left = Assign(left, right)
        return left

    def parse_orelse(self):
        left = self.parse_andalso()
        while self.lexer.peek()[1] == 'orelse':
            self.lexer.consume()
            right = self.parse_andalso()
            left = OrElse(left, right)
        return left

    def parse_andalso(self):
        left = self.parse_comp()
        while self.lexer.peek()[1] == 'andalso':
            self.lexer.consume()
            right = self.parse_comp()
            left = AndAlso(left, right)
        return left

    def parse_comp(self):
        left = self.parse_cons()
        t = self.lexer.peek()[1]
        if t in ['=', '<>', '<', '<=', '>', '>=']:
            op = self.lexer.consume()[1]
            right = self.parse_cons()
            if op == '=':
                return Eq(left, right)
            if op == '<>':
                return Neq(left, right)
            if op == '<':
                return Less(left, right)
            if op == '<=':
                return LessEq(left, right)
            if op == '>':
                return Greater(left, right)
            if op == '>=':
                return GreaterEq(left, right)
        return left

    def parse_cons(self):
        left = self.parse_arith()
        if self.lexer.peek()[1] == '::':
            self.lexer.consume()
            right = self.parse_cons()
            return Cons(left, right)
        return left

    def parse_arith(self):
        left = self.parse_term()
        while True:
            t = self.lexer.peek()[1]
            if t == '+':
                self.lexer.consume()
                left = Add(left, self.parse_term())
            elif t == '-':
                self.lexer.consume()
                left = Sub(left, self.parse_term())
            else:
                break
        return left

    def parse_term(self):
        left = self.parse_app()
        while True:
            t = self.lexer.peek()[1]
            if t == '*':
                self.lexer.consume()
                left = Mul(left, self.parse_app())
            elif t == '/':
                self.lexer.consume()
                left = Div(left, self.parse_app())
            elif t == '%':
                self.lexer.consume()
                left = Mod(left, self.parse_app())
            else:
                break
        return left

    def parse_app(self):
        left = self.parse_unary()
        while True:
            t = self.lexer.peek()
            if t[0] in ['NUM', 'ID'] or t[1] in ['(', 'true', 'false', 'nil', 'ref', 'not', '~', '!']:
                right = self.parse_unary()
                left = App(left, right)
            else:
                break
        return left

    def parse_unary(self):
        t = self.lexer.peek()
        if t[1] == 'not':
            self.lexer.consume()
            return Not(self.parse_unary())
        if t[1] == '~':
            self.lexer.consume()
            return Neg(self.parse_unary())
        if t[1] == '!':
            self.lexer.consume()
            return Deref(self.parse_unary())
        if t[1] == 'ref':
            self.lexer.consume()
            return Ref(self.parse_unary())
        return self.parse_atom()

    def parse_atom(self):
        t = self.lexer.consume()
        if t[0] == 'NUM':
            return IntegerLiteral(int(t[1]))
        if t[0] == 'ID':
            if t[1] == 'true':
                return BooleanLiteral(True)
            if t[1] == 'false':
                return BooleanLiteral(False)
            if t[1] == 'nil':
                return Nil()
            return Name(t[1])
        if t[1] == '(':
            if self.lexer.peek()[1] == ')':
                self.lexer.consume()
                return Unit()
            e = self.expr()
            if self.lexer.peek()[1] == ',':
                self.lexer.consume()
                e2 = self.expr()
                self.lexer.consume(val=')')
                return Pair(e, e2)
            self.lexer.consume(val=')')
            return Group(e)

        raise Exception(f"Unexpected token: {t}")
