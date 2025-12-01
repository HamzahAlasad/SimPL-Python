from simpl_interpreter import *
from simpl_ast import *
from simpl_typing import *

class fst(FunValue):
    def __init__(self):
        super().__init__(None, "x", Name("x"))
class snd(FunValue):
    def __init__(self):
        super().__init__(None, "x", Name("x"))
class hd(FunValue):
    def __init__(self):
        super().__init__(None, "x", Name("x"))
class tl(FunValue):
    def __init__(self):
        super().__init__(None, "x", Name("x"))

class succ(FunValue):
    def __init__(self):
        super().__init__(None, "x", Add(Name("x"), IntegerLiteral(1)))

class pred(FunValue):
    def __init__(self):
        super().__init__(None, "x", Sub(Name("x"), IntegerLiteral(1)))

class iszero(FunValue):
    def __init__(self):
        super().__init__(None, "x", Eq(Name("x"), IntegerLiteral(0)))

def initial_runtime_env():
    E = Env.empty()
    E = Env(E, "fst", fst())
    E = Env(E, "snd", snd())
    E = Env(E, "hd", hd())
    E = Env(E, "tl", tl())
    E = Env(E, "succ", succ())
    E = Env(E, "pred", pred())
    E = Env(E, "iszero", iszero())
    return E

def initial_type_env():
    E = TypeEnv.empty()
    a = TypeVar(True)
    b = TypeVar(True)
    E = ExtendedTypeEnv(E, "fst", ArrowType(PairType(a, b), a))
    E = ExtendedTypeEnv(E, "snd", ArrowType(PairType(a, b), b))
    E = ExtendedTypeEnv(E, "hd", ArrowType(ListType(a), a))
    E = ExtendedTypeEnv(E, "tl", ArrowType(ListType(a), ListType(a)))
    E = ExtendedTypeEnv(E, "iszero", ArrowType(Type.INT, Type.BOOL))
    E = ExtendedTypeEnv(E, "pred", ArrowType(Type.INT, Type.INT))
    E = ExtendedTypeEnv(E, "succ", ArrowType(Type.INT, Type.INT))
    return E