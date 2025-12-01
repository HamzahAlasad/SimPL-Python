from dataclasses import dataclass

class TypeError(Exception):
    pass

class TypeMismatchError(TypeError):
    def __init__(self):
        super().__init__("mismatch")

class TypeCircularityError(TypeError):
    def __init__(self):
        super().__init__("circular")

class Substitution:
    def apply(self, t):
        raise NotImplementedError()

    def compose(self, other):
        if hasattr(other, 'get'):
            return ComposedTypeEnv(self, other)
        return Compose(self, other)

@dataclass
class Identity(Substitution):
    def apply(self, t):
        return t
    def compose(self, other):
        return other

@dataclass
class Replace(Substitution):
    a: 'TypeVar'
    t: 'Type'
    
    def apply(self, b):
        return b.replace(self.a, self.t)

@dataclass
class Compose(Substitution):
    f: Substitution
    g: Substitution
    
    def apply(self, t):
        return self.f.apply(self.g.apply(t))

@dataclass
class TypeResult:
    s: Substitution
    t: 'Type'
    
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

@dataclass
class ExtendedTypeEnv(TypeEnv):
    E: TypeEnv
    x: str
    t: 'Type'
    
    def get(self, y):
        if self.x == y:
            return self.t
        return self.E.get(y)

@dataclass
class ComposedTypeEnv(TypeEnv):
    s: Substitution
    E: TypeEnv
    
    def get(self, x):
        t = self.E.get(x)
        if t is None: return None
        return self.s.apply(t)

class Type:
    def is_equality_type(self): raise NotImplementedError()
    def unify(self, t): raise NotImplementedError()
    def contains(self, tv): raise NotImplementedError()
    def replace(self, a, t): raise NotImplementedError()

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
    
    def is_equality_type(self): return self.equality_type
    
    def unify(self, t):
        if t is self: return Identity()
        if t.contains(self): raise TypeCircularityError()
        return Replace(self, t)
    
    def contains(self, tv): return self is tv
    
    def replace(self, a, t):
        if self is a: return t
        return self
    
    def __str__(self): return self.name

@dataclass
class ArrowType(Type):
    t1: Type
    t2: Type
    
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

@dataclass
class PairType(Type):
    t1: Type
    t2: Type
    
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

@dataclass
class ListType(Type):
    t: Type
    
    def is_equality_type(self): return self.t.is_equality_type()
    
    def unify(self, t):
        if isinstance(t, TypeVar): return t.unify(self)
        if isinstance(t, ListType): return self.t.unify(t.t)
        raise TypeMismatchError()
    
    def contains(self, tv): return self.t.contains(tv)
    def replace(self, a, t): return ListType(self.t.replace(a, t))
    def __str__(self): return f"{self.t} list"

@dataclass
class RefType(Type):
    t: Type
    
    def is_equality_type(self): return True
    
    def unify(self, t):
        if isinstance(t, TypeVar): return t.unify(self)
        if isinstance(t, RefType): return self.t.unify(t.t)
        raise TypeMismatchError()
    
    def contains(self, tv): return self.t.contains(tv)
    def replace(self, a, t): return RefType(self.t.replace(a, t))
    def __str__(self): return f"{self.t} ref"

Type.INT = IntType()
Type.BOOL = BoolType()
Type.UNIT = UnitType()