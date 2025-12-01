from dataclasses import dataclass


class RuntimeError(Exception):
    pass


class Value:
    pass


@dataclass
class IntValue(Value):
    n: int
    def __str__(self): return str(self.n)


@dataclass
class BoolValue(Value):
    b: bool
    def __str__(self): return str(self.b).lower()


class UnitValue(Value):
    def __str__(self): return "unit"
    def __eq__(self, other): return isinstance(other, UnitValue)


class NilValue(Value):
    def __str__(self): return "nil"
    def __eq__(self, other): return isinstance(other, NilValue)


@dataclass
class PairValue(Value):
    v1: Value
    v2: Value
    def __str__(self): return f"pair@{self.v1}@{self.v2}"


@dataclass
class ConsValue(Value):
    v1: Value
    v2: Value

    def __str__(self): return f"list@{self.length()}"

    def length(self):
        if isinstance(self.v2, NilValue):
            return 1
        if isinstance(self.v2, ConsValue):
            return 1 + self.v2.length()
        return 1


@dataclass
class RefValue(Value):
    p: int
    def __str__(self): return f"ref@{self.p}"


@dataclass
class FunValue(Value):
    E: 'Env'
    x: str
    e: 'Expr'
    def __str__(self): return "fun"
    def __eq__(self, other): return self is other


@dataclass
class RecValue(Value):
    E: 'Env'
    x: str
    e: 'Expr'
    def __eq__(self, other): return self is other


Value.UNIT = UnitValue()
Value.NIL = NilValue()


@dataclass
class Env:
    E: 'Env'
    x: str
    v: Value

    @staticmethod
    def empty(): return None

    def get(self, y):
        if self.x == y:
            return self.v
        if self.E is None:
            return None
        return self.E.get(y)

    def clone(self):
        return self


@dataclass
class Mem:
    map: dict = None

    def __post_init__(self):
        if self.map is None:
            self.map = {}

    def get(self, p): return self.map.get(p)
    def put(self, p, v): self.map[p] = v


@dataclass
class Int:
    n: int
    def get(self): return self.n
    def set(self, n): self.n = n


@dataclass
class State:
    E: Env
    M: Mem
    p: Int

    @staticmethod
    def of(E, M, p):
        return State(E, M, p)


class InitialState(State):
    pass
