from simpl_typing import *
from simpl_interpreter import *
from simpl_lib import *

class Expr:
    def typecheck(self, E): raise NotImplementedError()
    def eval(self, s): raise NotImplementedError()

class IntegerLiteral(Expr):
    def __init__(self, n): self.n = n
    def __str__(self): return str(self.n)
    def typecheck(self, E): return TypeResult.of(Identity(), Type.INT)
    def eval(self, s): return IntValue(self.n)

class BooleanLiteral(Expr):
    def __init__(self, b): self.b = b
    def __str__(self): return str(self.b).lower()
    def typecheck(self, E): return TypeResult.of(Identity(), Type.BOOL)
    def eval(self, s): return BoolValue(self.b)

class Unit(Expr):
    def __str__(self): return "()"
    def typecheck(self, E): return TypeResult.of(Identity(), Type.UNIT)
    def eval(self, s): return Value.UNIT

class Nil(Expr):
    def __str__(self): return "nil"
    def typecheck(self, E): return TypeResult.of(Identity(), ListType(TypeVar(True)))
    def eval(self, s): return Value.NIL

class Name(Expr):
    def __init__(self, x): self.x = x
    def __str__(self): return str(self.x)
    def typecheck(self, E):
        t = E.get(self.x)
        if t is None: raise TypeError(f"variable {self.x} not found")
        return TypeResult.of(Identity(), t)
    def eval(self, s):
        v = s.E.get(self.x)
        if v is None: raise RuntimeError(f"variable {self.x} not defined")
        if isinstance(v, RecValue):
            return Rec(v.x, v.e).eval(State.of(v.E, s.M, s.p))
        return v

class BinaryExpr(Expr):
    def __init__(self, l, r):
        self.l = l
        self.r = r

class Add(BinaryExpr):
    def __str__(self): return f"({self.l} + {self.r})"
    def typecheck(self, E):
        r1 = self.l.typecheck(E)
        r2 = self.r.typecheck(r1.s.compose(E))
        s = r2.s.compose(r1.s)
        s = s.compose(r1.t.unify(Type.INT))
        s = s.compose(r2.t.unify(Type.INT))
        return TypeResult.of(s, Type.INT)
    def eval(self, s):
        return IntValue(self.l.eval(s).n + self.r.eval(s).n)

class Sub(BinaryExpr):
    def __str__(self): return f"({self.l} - {self.r})"
    def typecheck(self, E):
        r1 = self.l.typecheck(E)
        r2 = self.r.typecheck(r1.s.compose(E))
        s = r2.s.compose(r1.s)
        s = s.compose(r1.t.unify(Type.INT))
        s = s.compose(r2.t.unify(Type.INT))
        return TypeResult.of(s, Type.INT)
    def eval(self, s):
        return IntValue(self.l.eval(s).n - self.r.eval(s).n)

class Mul(BinaryExpr):
    def __str__(self): return f"({self.l} * {self.r})"
    def typecheck(self, E):
        r1 = self.l.typecheck(E)
        r2 = self.r.typecheck(r1.s.compose(E))
        s = r2.s.compose(r1.s)
        s = s.compose(r1.t.unify(Type.INT))
        s = s.compose(r2.t.unify(Type.INT))
        return TypeResult.of(s, Type.INT)
    def eval(self, s):
        return IntValue(self.l.eval(s).n * self.r.eval(s).n)

class Div(BinaryExpr):
    def __str__(self): return f"({self.l} / {self.r})"
    def typecheck(self, E):
        r1 = self.l.typecheck(E)
        r2 = self.r.typecheck(r1.s.compose(E))
        s = r2.s.compose(r1.s)
        s = s.compose(r1.t.unify(Type.INT))
        s = s.compose(r2.t.unify(Type.INT))
        return TypeResult.of(s, Type.INT)
    def eval(self, s):
        v2 = self.r.eval(s).n
        if v2 == 0: raise RuntimeError("Division by zero")
        return IntValue(int(self.l.eval(s).n / v2))

class Mod(BinaryExpr):
    def __str__(self): return f"({self.l} % {self.r})"
    def typecheck(self, E):
        r1 = self.l.typecheck(E)
        r2 = self.r.typecheck(r1.s.compose(E))
        s = r2.s.compose(r1.s)
        s = s.compose(r1.t.unify(Type.INT))
        s = s.compose(r2.t.unify(Type.INT))
        return TypeResult.of(s, Type.INT)
    def eval(self, s):
        v2 = self.r.eval(s).n
        if v2 == 0: raise RuntimeError("Division by zero")
        return IntValue(self.l.eval(s).n % v2)

class Eq(BinaryExpr):
    def __str__(self): return f"({self.l} = {self.r})"
    def typecheck(self, E):
        r1 = self.l.typecheck(E)
        r2 = self.r.typecheck(r1.s.compose(E))
        s = r2.s.compose(r1.s)
        s = s.compose(r1.t.unify(r2.t))
        if not s.apply(r1.t).is_equality_type():
            raise TypeError("Equality test on non-equality type")
        return TypeResult.of(s, Type.BOOL)
    def eval(self, s):
        return BoolValue(self.l.eval(s) == self.r.eval(s))

class Neq(BinaryExpr):
    def __str__(self): return f"({self.l} <> {self.r})"
    def typecheck(self, E):
        r1 = self.l.typecheck(E)
        r2 = self.r.typecheck(r1.s.compose(E))
        s = r2.s.compose(r1.s)
        s = s.compose(r1.t.unify(r2.t))
        if not s.apply(r1.t).is_equality_type():
            raise TypeError("Equality test on non-equality type")
        return TypeResult.of(s, Type.BOOL)
    def eval(self, s):
        return BoolValue(not (self.l.eval(s) == self.r.eval(s)))

class Less(BinaryExpr):
    def __str__(self): return f"({self.l} < {self.r})"
    def typecheck(self, E):
        r1 = self.l.typecheck(E)
        r2 = self.r.typecheck(r1.s.compose(E))
        s = r2.s.compose(r1.s)
        s = s.compose(r1.t.unify(Type.INT))
        s = s.compose(r2.t.unify(Type.INT))
        return TypeResult.of(s, Type.BOOL)
    def eval(self, s):
        return BoolValue(self.l.eval(s).n < self.r.eval(s).n)

class LessEq(BinaryExpr):
    def __str__(self): return f"({self.l} <= {self.r})"
    def typecheck(self, E):
        r1 = self.l.typecheck(E)
        r2 = self.r.typecheck(r1.s.compose(E))
        s = r2.s.compose(r1.s)
        s = s.compose(r1.t.unify(Type.INT))
        s = s.compose(r2.t.unify(Type.INT))
        return TypeResult.of(s, Type.BOOL)
    def eval(self, s):
        return BoolValue(self.l.eval(s).n <= self.r.eval(s).n)

class Greater(BinaryExpr):
    def __str__(self): return f"({self.l} > {self.r})"
    def typecheck(self, E):
        r1 = self.l.typecheck(E)
        r2 = self.r.typecheck(r1.s.compose(E))
        s = r2.s.compose(r1.s)
        s = s.compose(r1.t.unify(Type.INT))
        s = s.compose(r2.t.unify(Type.INT))
        return TypeResult.of(s, Type.BOOL)
    def eval(self, s):
        return BoolValue(self.l.eval(s).n > self.r.eval(s).n)

class GreaterEq(BinaryExpr):
    def __str__(self): return f"({self.l} >= {self.r})"
    def typecheck(self, E):
        r1 = self.l.typecheck(E)
        r2 = self.r.typecheck(r1.s.compose(E))
        s = r2.s.compose(r1.s)
        s = s.compose(r1.t.unify(Type.INT))
        s = s.compose(r2.t.unify(Type.INT))
        return TypeResult.of(s, Type.BOOL)
    def eval(self, s):
        return BoolValue(self.l.eval(s).n >= self.r.eval(s).n)

class AndAlso(BinaryExpr):
    def __str__(self): return f"({self.l} andalso {self.r})"
    def typecheck(self, E):
        r1 = self.l.typecheck(E)
        r2 = self.r.typecheck(r1.s.compose(E))
        s = r2.s.compose(r1.s)
        s = s.compose(r1.t.unify(Type.BOOL))
        s = s.compose(r2.t.unify(Type.BOOL))
        return TypeResult.of(s, Type.BOOL)
    def eval(self, s):
        v1 = self.l.eval(s)
        if not v1.b: return BoolValue(False)
        return BoolValue(self.r.eval(s).b)

class OrElse(BinaryExpr):
    def __str__(self): return f"({self.l} orelse {self.r})"
    def typecheck(self, E):
        r1 = self.l.typecheck(E)
        r2 = self.r.typecheck(r1.s.compose(E))
        s = r2.s.compose(r1.s)
        s = s.compose(r1.t.unify(Type.BOOL))
        s = s.compose(r2.t.unify(Type.BOOL))
        return TypeResult.of(s, Type.BOOL)
    def eval(self, s):
        v1 = self.l.eval(s)
        if v1.b: return BoolValue(True)
        return BoolValue(self.r.eval(s).b)

class Pair(BinaryExpr):
    def __str__(self): return f"(pair {self.l} {self.r})"
    def typecheck(self, E):
        r1 = self.l.typecheck(E)
        r2 = self.r.typecheck(r1.s.compose(E))
        return TypeResult.of(r2.s.compose(r1.s), PairType(r1.t, r2.t))
    def eval(self, s):
        return PairValue(self.l.eval(s), self.r.eval(s))

class Cons(BinaryExpr):
    def __str__(self): return f"({self.l} :: {self.r})"
    def typecheck(self, E):
        r1 = self.l.typecheck(E)
        r2 = self.r.typecheck(r1.s.compose(E))
        s = r2.s.compose(r1.s)
        s = s.compose(r2.t.unify(ListType(r1.t)))
        return TypeResult.of(s, s.apply(r2.t))
    def eval(self, s):
        return ConsValue(self.l.eval(s), self.r.eval(s))

class Seq(BinaryExpr):
    def __str__(self): return f"({self.l} ; {self.r})"
    def typecheck(self, E):
        r1 = self.l.typecheck(E)
        r2 = self.r.typecheck(r1.s.compose(E))
        return TypeResult.of(r2.s.compose(r1.s), r2.t)
    def eval(self, s):
        self.l.eval(s)
        return self.r.eval(s)

class Assign(BinaryExpr):
    def __str__(self): return f"{self.l} := {self.r}"
    def typecheck(self, E):
        r1 = self.l.typecheck(E)
        r2 = self.r.typecheck(r1.s.compose(E))
        s = r2.s.compose(r1.s)
        s = s.compose(r1.t.unify(RefType(r2.t)))
        return TypeResult.of(s, Type.UNIT)
    def eval(self, s):
        ptr = self.l.eval(s)
        val = self.r.eval(s)
        s.M.put(ptr.p, val)
        return Value.UNIT

class App(BinaryExpr):
    def __str__(self): return f"({self.l} {self.r})"
    def typecheck(self, E):
        alpha = TypeVar(False)
        r1 = self.l.typecheck(E)
        r2 = self.r.typecheck(E)
        s = r2.s.compose(r1.s)
        s_unify = ArrowType(r2.t, alpha).unify(r1.t)
        s = s_unify.compose(s)
        return TypeResult.of(s, s.apply(alpha))
    
    def eval(self, s):
        f = self.l.eval(s)
        v = self.r.eval(s)
        
        if isinstance(f, fst): return v.v1
        if isinstance(f, snd): return v.v2
        if isinstance(f, hd):
            if isinstance(v, NilValue): raise RuntimeError("hd of nil")
            return v.v1
        if isinstance(f, tl):
            if isinstance(v, NilValue): raise RuntimeError("tl of nil")
            return v.v2
            
        new_env = Env(f.E, f.x, v)
        return f.e.eval(State.of(new_env, s.M, s.p))

class UnaryExpr(Expr):
    def __init__(self, e): self.e = e

class Neg(UnaryExpr):
    def __str__(self): return f"~{self.e}"
    def typecheck(self, E):
        r = self.e.typecheck(E)
        s = r.t.unify(Type.INT)
        return TypeResult.of(s.compose(r.s), Type.INT)
    def eval(self, s):
        return IntValue(-self.e.eval(s).n)

class Not(UnaryExpr):
    def __str__(self): return f"(not {self.e})"
    def typecheck(self, E):
        r = self.e.typecheck(E)
        s = r.t.unify(Type.BOOL)
        return TypeResult.of(s.compose(r.s), Type.BOOL)
    def eval(self, s):
        return BoolValue(not self.e.eval(s).b)

class Ref(UnaryExpr):
    def __str__(self): return f"(ref {self.e})"
    def typecheck(self, E):
        r = self.e.typecheck(E)
        return TypeResult.of(r.s, RefType(r.t))
    def eval(self, s):
        ptr = s.p.get()
        s.p.set(ptr + 1)
        v = self.e.eval(s)
        s.M.put(ptr, v)
        return RefValue(ptr)

class Deref(UnaryExpr):
    def __str__(self): return f"!{self.e}"
    def typecheck(self, E):
        r = self.e.typecheck(E)
        alpha = TypeVar(True)
        s = r.t.unify(RefType(alpha))
        return TypeResult.of(s.compose(r.s), s.apply(alpha))
    def eval(self, s):
        ptr = self.e.eval(s)
        v = s.M.get(ptr.p)
        if v is None: raise RuntimeError("Segmentation fault")
        return v

class Group(UnaryExpr):
    def __str__(self): return str(self.e)
    def typecheck(self, E): return self.e.typecheck(E)
    def eval(self, s): return self.e.eval(s)

class Cond(Expr):
    def __init__(self, e1, e2, e3):
        self.e1 = e1; self.e2 = e2; self.e3 = e3
    def __str__(self): return f"(if {self.e1} then {self.e2} else {self.e3})"
    def typecheck(self, E):
        r1 = self.e1.typecheck(E)
        s1 = r1.t.unify(Type.BOOL)
        env2 = s1.compose(r1.s).compose(E)
        r2 = self.e2.typecheck(env2)
        r3 = self.e3.typecheck(r2.s.compose(env2))
        s2 = r2.t.unify(r2.s.apply(r3.t))
        all_s = s2.compose(r3.s).compose(r2.s).compose(s1).compose(r1.s)
        return TypeResult.of(all_s, all_s.apply(r2.t))
    def eval(self, s):
        if self.e1.eval(s).b: return self.e2.eval(s)
        else: return self.e3.eval(s)

class Loop(Expr):
    def __init__(self, e1, e2):
        self.e1 = e1; self.e2 = e2
    def __str__(self): return f"(while {self.e1} do {self.e2})"
    def typecheck(self, E):
        r1 = self.e1.typecheck(E)
        s1 = r1.t.unify(Type.BOOL)
        r2 = self.e2.typecheck(s1.compose(r1.s).compose(E))
        return TypeResult.of(r2.s.compose(r1.s), Type.UNIT)
    def eval(self, s):
        while self.e1.eval(s).b:
            self.e2.eval(s)
        return Value.UNIT

class Let(Expr):
    def __init__(self, x, e1, e2):
        self.x = x; self.e1 = e1; self.e2 = e2
    def __str__(self): return f"(let {self.x} = {self.e1} in {self.e2})"
    def typecheck(self, E):
        r1 = self.e1.typecheck(E)
        new_env = ExtendedTypeEnv(E, self.x, r1.t)
        r2 = self.e2.typecheck(new_env)
        return TypeResult.of(r2.s.compose(r1.s), r2.s.apply(r2.t))
    def eval(self, s):
        v1 = self.e1.eval(s)
        return self.e2.eval(State.of(Env(s.E, self.x, v1), s.M, s.p))

class Fn(Expr):
    def __init__(self, x, e):
        self.x = x; self.e = e
    def __str__(self): return f"(fn {self.x}.{self.e})"
    def typecheck(self, E):
        t = TypeVar(True)
        new_env = ExtendedTypeEnv(E, self.x, t)
        r = self.e.typecheck(new_env)
        return TypeResult.of(r.s, ArrowType(r.s.apply(t), r.t))
    def eval(self, s):
        return FunValue(s.E, self.x, self.e)

class Rec(Expr):
    def __init__(self, x, e):
        self.x = x; self.e = e
    def __str__(self): return f"(rec {self.x}.{self.e})"
    def typecheck(self, E):
        alpha = TypeVar(True)
        new_env = ExtendedTypeEnv(E, self.x, alpha)
        r = self.e.typecheck(new_env)
        s = r.s.compose(r.t.unify(r.s.apply(alpha)))
        return TypeResult.of(s, s.apply(r.t))
    def eval(self, s):
        rv = RecValue(s.E, self.x, self.e)
        return self.e.eval(State.of(Env(s.E, self.x, rv), s.M, s.p))