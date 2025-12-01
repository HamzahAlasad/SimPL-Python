class RuntimeError(Exception):
    pass

class Value:
    pass

class IntValue(Value):
    def __init__(self, n): self.n = n
    def __str__(self): return str(self.n)
    def __eq__(self, other): return isinstance(other, IntValue) and self.n == other.n

class BoolValue(Value):
    def __init__(self, b): self.b = b
    def __str__(self): return str(self.b).lower()
    def __eq__(self, other): return isinstance(other, BoolValue) and self.b == other.b

class UnitValue(Value):
    def __str__(self): return "unit"
    def __eq__(self, other): return isinstance(other, UnitValue)

class NilValue(Value):
    def __str__(self): return "nil"
    def __eq__(self, other): return isinstance(other, NilValue)

class PairValue(Value):
    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2
    def __str__(self): return f"pair@{self.v1}@{self.v2}"
    def __eq__(self, other):
        return isinstance(other, PairValue) and self.v1 == other.v1 and self.v2 == other.v2

class ConsValue(Value):
    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2
    
    def __str__(self): return f"list@{self.length()}"
    
    def length(self):
        if isinstance(self.v2, NilValue): return 1
        if isinstance(self.v2, ConsValue): return 1 + self.v2.length()
        return 1
    
    def __eq__(self, other):
        return isinstance(other, ConsValue) and self.v1 == other.v1 and self.v2 == other.v2

class RefValue(Value):
    def __init__(self, p): self.p = p
    def __str__(self): return f"ref@{self.p}"
    def __eq__(self, other): return isinstance(other, RefValue) and self.p == other.p

class FunValue(Value):
    def __init__(self, E, x, e):
        self.E = E
        self.x = x
        self.e = e
    def __str__(self): return "fun"
    def __eq__(self, other): return self is other

class RecValue(Value):
    def __init__(self, E, x, e):
        self.E = E
        self.x = x
        self.e = e
    def __eq__(self, other): return self is other

# Statics
Value.UNIT = UnitValue()
Value.NIL = NilValue()

class Env:
    def __init__(self, E, x, v):
        self.E = E
        self.x = x
        self.v = v

    @staticmethod
    def empty(): return None
    
    def get(self, y):
        if self.x == y: return self.v
        if self.E is None: return None
        return self.E.get(y)
    
    def clone(self):
        return self

class Mem:
    def __init__(self):
        self.map = {}
    def get(self, p): return self.map.get(p)
    def put(self, p, v): self.map[p] = v

class Int:
    def __init__(self, n): self.n = n
    def get(self): return self.n
    def set(self, n): self.n = n

class State:
    def __init__(self, E, M, p):
        self.E = E
        self.M = M
        self.p = p
    
    @staticmethod
    def of(E, M, p):
        return State(E, M, p)

class InitialState(State):
    pass