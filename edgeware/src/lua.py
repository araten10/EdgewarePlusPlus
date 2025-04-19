if __name__ == "__main__":
    import os

    from paths import Data

    # Required on Windows
    os.environ["PATH"] += os.pathsep + str(Data.ROOT)

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

# stat ::= Name ‘=’ exp |
#          break |
#          do block end |
#          repeat block until exp |
#          if exp then block {elseif exp then block} [else block] end |
#          for Name ‘=’ exp ‘,’ exp [‘,’ exp] do block end |
#          for parse_name_list in parse_expression_list do block end |
#          function Name FunctionBody |

# exp ::=  ‘(’ exp ‘)’ | exp binop exp | unop exp

# binop ::=  ‘+’ | ‘-’ | ‘*’ | ‘/’ | ‘//’ | ‘^’ | ‘%’ | ‘..’ | ‘<’ | ‘<=’ |
#            ‘>’ | ‘>=’ | ‘==’ | ‘~=’ | and | or

# unop ::= ‘-’ | not | ‘#’

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


# TODO: Global variables, proper error messages, don't allow defining keywords
class Environment:
    def __init__(self, local: dict[str, Any] = {}, external: Environment | None = None):
        self.local = local
        self.external = external

    def find(self, name: str) -> Environment:
        return self if name in self.local else self.external.find(name)

    def get(self, name: str) -> Any:
        return self.find(name).local[name]

    def define(self, name: str, value: Any) -> None:
        self.local[name] = value

    def assign(self, name: str, value: Any) -> None:
        self.find(name).local[name] = value


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
        return lambda *args: self.block.eval(Environment(dict(zip(self.params, args)), env))


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
    def __init__(self, tokens: Tokens):
        for token, value in [("nil", None), ("false", False), ("true", True)]:
            if tokens.skip_if(token):
                self.eval = lambda env: value
                return

        for numeral in [int, float]:
            try:
                number = numeral(tokens.next)
                tokens.skip()
                self.eval = lambda env: number
                return
            except ValueError:
                pass

        if tokens.next[0] == '"' and tokens.next[-1] == '"':
            string = tokens.get()
            self.eval = lambda env: string[1:-1]
            return

        if tokens.ahead == "(":
            call = FunctionCall(tokens)
            self.eval = lambda env: call.eval(env)
            return

        name = tokens.get_name()
        self.eval = lambda env: env.get(name)


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

    def eval(self, env: Environment) -> ReturnValue | None:
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
