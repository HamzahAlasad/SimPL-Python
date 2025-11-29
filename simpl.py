import sys
from simpl_parser import Lexer, Parser
from simpl_interpreter import InitialState, Mem, Int, RuntimeError
from simpl_typing import DefaultTypeEnv, TypeError, TypeCircularityError
from simpl_library import initial_runtime_env, initial_type_env

def run(filename):
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        lexer = Lexer(content)
        parser = Parser(lexer)
        program = parser.parse()
        
        program.typecheck(initial_type_env())
        
        v = program.eval(InitialState.of(initial_runtime_env(), Mem(), Int(0)))
        
        print(v)
        
    except RuntimeError as e:
        print("runtime error")
    except (TypeError, TypeCircularityError) as e:
        print("type error")
    except Exception as e:

        print("syntax error")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run(sys.argv[1])
    else:
        print("Usage: python simpl.py <filename>")