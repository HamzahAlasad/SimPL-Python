class TypeError(Exception):
    pass

class TypeMismatchError(TypeError):
    def __init__(self):
        super().__init__("type mismatch")

class TypeCircularityError(TypeError):
    def __init__(self):
        super().__init__("circular type")

class Substitution:
    def apply(self, t):
        raise NotImplementedError()

    def compose(self, other):
        return Compose(self, other)

class Identity(Substitution):
    def apply(self, t):
        return t

class Replace(Substitution):
    def __init__(self, a, t):
        self.a = a
        self.t = t
    
    def apply(self, b):
        return b.replace(self.a, self.t)

class Compose(Substitution):
    def __init__(self, f, g):
        self.f = f
        self.g = g
    
    def apply(self, t):
        return self.f.apply(self.g.apply(t))

class TypeResult:
    def __init__(self, s, t):
        self.s = s
        self.t = t
    
    @staticmethod
    def of(s, t):
        return TypeResult(s, t)

class TypeEnv:
    def get(self, x):
        raise NotImplementedError()
    
    @staticmethod
    def empty():
        return EmptyTypeEnv()
    
    @staticmethod
    def of(E, x, t):
        return ExtendedTypeEnv(E, x, t)

class EmptyTypeEnv(TypeEnv):
    def get(self, x):
        return None

class ExtendedTypeEnv(TypeEnv):
    def __init__(self, E, x, t):
        self.E = E
        self.x = x
        self.t = t
    
    def get(self, y):
        if self.x == y:
            return self.t
        return self.E.get(y)

# tyees

class Type:
    def is_equality_type(self):
        raise NotImplementedError()
    
    def unify(self, t):
        raise NotImplementedError()
    
    def contains(self, tv):
        raise NotImplementedError()
    
    def replace(self, a, t):
        raise NotImplementedError()

class IntType(Type):
    def is_equality_type(self): return True
    
    def unify(self, t):
        if isinstance(t, TypeVar): return t.unify(self)
        if isinstance(t, IntType): return Identity()
        raise TypeMismatchError()
    
    def contains(self, tv): return False
    def replace(self, a, t): return self
    def __str__(self): return "int"

class BoolType(Type):
    def is_equality_type(self): return True
    
    def unify(self, t):
        if isinstance(t, TypeVar): return t.unify(self)
        if isinstance(t, BoolType): return Identity()
        raise TypeMismatchError()
    
    def contains(self, tv): return False
    def replace(self, a, t): return self
    def __str__(self): return "bool"

class UnitType(Type):
    def is_equality_type(self): return False
    
    def unify(self, t):
        if isinstance(t, TypeVar): return t.unify(self)
        if isinstance(t, UnitType): return Identity()
        raise TypeMismatchError()
    
    def contains(self, tv): return False
    def replace(self, a, t): return self
    def __str__(self): return "unit"

class TypeVar(Type):
    _tvcnt = 0
    
    def __init__(self, equality_type):
        self.equality_type = equality_type
        TypeVar._tvcnt += 1
        self.name = f"tv{TypeVar._tvcnt}"
    
    def is_equality_type(self):
        return self.equality_type
    
    def unify(self, t):
        if t is self: return Identity()
        if t.contains(self): raise TypeCircularityError()
        return Replace(self, t)
    
    def contains(self, tv): return self is tv
    
    def replace(self, a, t):
        if self is a: return t
        return self
    
    def __str__(self): return self.name

class ArrowType(Type):
    def __init__(self, t1, t2):
        self.t1 = t1
        self.t2 = t2
    
    def is_equality_type(self): return False
    
    def unify(self, t):
        if isinstance(t, TypeVar): return t.unify(self)
        if isinstance(t, ArrowType):
            s1 = self.t1.unify(t.t1)
            s2 = s1.apply(self.t2).unify(s1.apply(t.t2))
            return s2.compose(s1)
        raise TypeMismatchError()
    
    def contains(self, tv): return self.t1.contains(tv) or self.t2.contains(tv)
    def replace(self, a, t): return ArrowType(self.t1.replace(a, t), self.t2.replace(a, t))
    def __str__(self): return f"({self.t1} -> {self.t2})"

class PairType(Type):
    def __init__(self, t1, t2):
        self.t1 = t1
        self.t2 = t2
    
    def is_equality_type(self): return self.t1.is_equality_type() and self.t2.is_equality_type()
    
    def unify(self, t):
        if isinstance(t, TypeVar): return t.unify(self)
        if isinstance(t, PairType):
            s1 = self.t1.unify(t.t1)
            s2 = s1.apply(self.t2).unify(s1.apply(t.t2))
            return s2.compose(s1)
        raise TypeMismatchError()
    
    def contains(self, tv): return self.t1.contains(tv) or self.t2.contains(tv)
    def replace(self, a, t): return PairType(self.t1.replace(a, t), self.t2.replace(a, t))
    def __str__(self): return f"({self.t1} * {self.t2})"

class ListType(Type):
    def __init__(self, t):
        self.t = t
    
    def is_equality_type(self): return self.t.is_equality_type()
    
    def unify(self, t):
        if isinstance(t, TypeVar): return t.unify(self)
        if isinstance(t, ListType): return self.t.unify(t.t)
        raise TypeMismatchError()
    
    def contains(self, tv): return self.t.contains(tv)
    def replace(self, a, t): return ListType(self.t.replace(a, t))
    def __str__(self): return f"{self.t} list"

class RefType(Type):
    def __init__(self, t):
        self.t = t
    
    def is_equality_type(self): return True
    
    def unify(self, t):
        if isinstance(t, TypeVar): return t.unify(self)
        if isinstance(t, RefType): return self.t.unify(t.t)
        raise TypeMismatchError()
    
    def contains(self, tv): return self.t.contains(tv)
    def replace(self, a, t): return RefType(self.t.replace(a, t))
    def __str__(self): return f"{self.t} ref"

# statics
Type.INT = IntType()
Type.BOOL = BoolType()
Type.UNIT = UnitType()