if __name__ == "__main__":
    import os

    from paths import Data

    # Required on Windows
    os.environ["PATH"] += os.pathsep + str(Data.ROOT)

import operator
import sys
from dataclasses import dataclass
from tkinter import Tk
from typing import Any, Callable

from pack import Pack
from pygame import mixer
from settings import Settings
from state import State

# chunk ::= block

# block ::= {stat} [retstat]

# stat ::= break |
#          do block end |
#          repeat block until exp |
#          if exp then block {elseif exp then block} [else block] end |
#          for Name ‘=’ exp ‘,’ exp [‘,’ exp] do block end |
#          for parse_name_list in parse_expression_list do block end |
#          function Name FunctionBody |

# binop ::= ‘..’

# unop ::= ‘#’

root = Tk()
root.withdraw()
settings = Settings()
pack = Pack(settings.pack_path)
state = State()

mixer.init()
mixer.set_num_channels(settings.max_audio)

script = """
local function hello(what)
  print("Hello", what)
end

local world = "world!"
hello(world)
"""


class Tokens(list[str]):
    def __init__(self, code: str):
        # TODO: Tokenize operators
        super().__init__()
        chars = list(code)
        special = ["(", ")", ","]

        while chars:
            if chars[0:2] == ["-", "-"]:
                terminate = ["]", "]"] if chars[2:4] == ["[", "["] else ["\n"]
                while chars[0 : len(terminate)] != terminate:
                    chars.pop(0)
                del chars[0 : len(terminate)]
                continue

            char = chars.pop(0)
            if char.isspace():
                continue
            elif char in special:
                self.append(char)
            elif char == '"':
                token = char
                while chars[0] != '"':
                    char = chars.pop(0)
                    token += chars.pop(0) if char == "\\" else char  # TODO: Proper escape sequences
                token += chars.pop(0)
                self.append(token)
            else:
                token = char
                while not (chars[0].isspace() or chars[0] in special):
                    token += chars.pop(0)
                self.append(token)

        self.append("end")

    @property
    def next(self) -> str:
        return self[0]

    @property
    def ahead(self) -> str:
        return self[1]

    def get(self) -> str:
        return self.pop(0)

    def get_name(self) -> str:
        if not all([char.isalnum() or char == "_" for char in self.next]) or self.next[0].isdigit():
            raise Exception(f"Invalid name {self.next}")
        return self.get()

    def skip(self, expected: str | None = None) -> None:
        token = self.get()
        if token != expected and expected:
            raise Exception(f"Unexpected token {token}, expected {expected}")

    def skip_if(self, possible: str) -> bool:
        if self.next == possible:
            self.skip()
            return True
        return False


class Environment:
    pass


# TODO: Don't allow defining keywords
class Environment:
    def __init__(self, scope: dict[str, Any], external: Environment | None = None, closure: set[str] | None = None):
        self.scope = scope
        self.external = external
        self.closure = closure

    def is_global(self) -> bool:
        return self.external is None

    def find(self, name: str, closure: set[str] | None = None) -> dict[str, Any]:
        if self.is_global():
            return self.scope

        in_scope = name in self.scope and (closure is None or name in closure)
        next_closure = closure if closure is not None else self.closure
        return self.scope if in_scope else self.external.find(name, next_closure)

    def get(self, name: str) -> Any:
        return self.find(name).get(name)

    def define(self, name: str, value: Any) -> None:
        self.scope[name] = value

    def assign(self, name: str, value: Any) -> None:
        self.find(name)[name] = value


class NameList(list[str]):
    def __init__(self, tokens: Tokens):
        super().__init__()
        self.append(tokens.get_name())
        while tokens.skip_if(","):
            self.append(tokens.get_name())


class Expression:
    pass


class ExpressionList(list[Expression]):
    def __init__(self, tokens: Tokens):
        super().__init__()
        self.append(Expression(tokens))
        while tokens.skip_if(","):
            self.append(Expression(tokens))


@dataclass
class ReturnValue:
    value: Any


class FunctionBody:
    def __init__(self, tokens: Tokens):
        tokens.skip("(")
        self.params = []
        if not tokens.skip_if(")"):
            self.params = NameList(tokens)
            tokens.skip(")")
        self.block = Block(tokens, "end")

    def eval(self, env: Environment) -> Callable:
        closure = set()
        lexical = env
        while not lexical.is_global():
            for name in lexical.scope:
                closure.add(name)
            lexical = lexical.external

        return lambda *args: self.block.eval(Environment(dict(zip(self.params, args)), env, closure))


class FunctionCall:
    def __init__(self, tokens: Tokens):
        self.name = tokens.get_name()
        tokens.skip("(")
        self.args = []
        if not tokens.skip_if(")"):
            self.args = ExpressionList(tokens)
            tokens.skip(")")

    def eval(self, env: Environment) -> Any:
        value = env.get(self.name)(*[arg.eval(env) for arg in self.args])
        if isinstance(value, ReturnValue):
            return value.value


class Expression:
    def __init__(self, tokens: Tokens, n_ary: bool = True):
        self.parts = [self.unary(tokens)]
        if not n_ary:
            return

        # TODO: Precedence
        binary_ops = {
            "+": operator.add,
            "-": operator.sub,
            "*": operator.mul,
            "/": operator.truediv,
            "//": operator.floordiv,
            "^": operator.pow,
            "%": operator.mod,
            "<": operator.lt,
            "<=": operator.le,
            ">": operator.gt,
            ">=": operator.ge,
            "==": operator.eq,
            "~=": operator.ne,
            "and": operator.and_,
            "or": operator.or_,
        }
        while tokens.next in binary_ops:
            op = binary_ops[tokens.get()]
            exp = Expression(tokens, False)
            self.parts.append(op)
            self.parts.append(exp.eval)

    def unary(self, tokens: Tokens) -> Callable:
        constants = {"nil": None, "false": False, "true": True}
        for token, value in constants.items():
            if tokens.skip_if(token):
                return lambda env: value

        for numeral in [int, float]:
            try:
                number = numeral(tokens.next)
                tokens.skip()
                return lambda env: number
            except ValueError:
                pass

        if tokens.next[0] == '"' and tokens.next[-1] == '"':
            string = tokens.get()
            self.eval = lambda env: string[1:-1]
            return

        if tokens.skip_if("("):
            exp = Expression(tokens)
            tokens.skip(")")
            return exp.eval

        unary_ops = {"-": operator.neg, "not": operator.not_}
        if tokens.next in unary_ops:
            op = unary_ops[tokens.get()]
            exp = Expression(tokens)
            return lambda env: op(exp.eval(env))

        if tokens.ahead == "(":
            call = FunctionCall(tokens)
            return lambda env: call.eval(env)

        name = tokens.get_name()
        return lambda env: env.get(name)

    def eval(self, env: Environment) -> Any:
        parts = self.parts.copy()

        exp_eval = parts.pop(0)
        value = exp_eval(env)
        while parts:
            op = parts.pop(0)
            exp_eval = parts.pop(0)
            value = op(value, exp_eval(env))
        return value


class Statement:
    def __init__(self, tokens: Tokens):
        match tokens.next:
            case "while":
                tokens.skip("while")
                test_exp = Expression(tokens)
                tokens.skip("do")
                block = Block(tokens, "end")

                def while_eval(env: Environment) -> ReturnValue | None:
                    while test_exp.eval(env):
                        value = block.eval(env)
                        if isinstance(value, ReturnValue):
                            return value

                self.eval = while_eval
                return
            case "if":
                tokens.skip("if")
                test_exp = Expression(tokens)
                tokens.skip("then")
                then_block = Block(tokens, "end")
                self.eval = lambda env: then_block.eval(env) if test_exp.eval(env) else None
                return
            case "local":
                tokens.skip("local")
                if tokens.skip_if("function"):
                    name = tokens.get_name()
                    body = FunctionBody(tokens)
                    self.eval = lambda env: env.define(name, body.eval(env))
                    return
                else:
                    name = tokens.get_name()
                    tokens.skip("=")
                    value = Expression(tokens)
                    self.eval = lambda env: env.define(name, value.eval(env))
                    return

        if tokens.ahead == "(":
            call = FunctionCall(tokens)
            self.eval = lambda env: call.eval(env)
            return

        name = tokens.get_name()
        tokens.skip("=")
        value = Expression(tokens)
        self.eval = lambda env: env.assign(name, value.eval(env))


class ReturnExpression:
    def eval(self, env: Environment) -> None:
        return


class Block:
    def __init__(self, tokens: Tokens, terminate: str):
        self.statements = []
        self.return_exp = None

        while tokens.next not in [terminate, "return"]:
            self.statements.append(Statement(tokens))

        if tokens.skip_if("return"):
            self.return_exp = Expression(tokens) if tokens.next != terminate else ReturnExpression()
        tokens.skip(terminate)

    def eval(self, external: Environment) -> ReturnValue | None:
        env = Environment({}, external)
        for statement in self.statements:
            value = statement.eval(env)
            if isinstance(value, ReturnValue):
                return value

        if self.return_exp is not None:
            return ReturnValue(self.return_exp.eval(env))


env = Environment({"print": lambda *args: print(*args)})
tokens = Tokens(script)
block = Block(tokens, "end")
block.eval(env)

root.after(1000, sys.exit)
root.mainloop()
