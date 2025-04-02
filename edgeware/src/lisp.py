import operator
import sys
from tkinter import Tk
from typing import Callable

from features.image_popup import ImagePopup
from features.misc import (
    display_notification,
    open_web,
    play_audio,
)
from features.subliminal_message_popup import SubliminalMessagePopup
from features.video_popup import VideoPopup
from pack import Pack
from pygame import mixer
from settings import Settings
from state import State

root = Tk()
root.withdraw()
settings = Settings()
pack = Pack(settings.pack_path)
state = State()

mixer.init()
mixer.set_num_channels(settings.max_audio)

script = """
(import (standard "1.0")
        (edgeware "1.0"))
(print "Hello world!")
"""

# Forward declarations
type Expression = object
type Environment = object


class String(str):
    pass


class Symbol(str):
    def __init__(self, name: str):
        special = ["+", "-", ".", "*", "/", "<", "=", ">", "!", "?", ":", "$", "%", "_", "&", "~", "^"]
        for char in name:
            if not (char.isalnum() or char in special):
                raise Exception(f"Invalid character {char} in symbol {name}")


class Procedure:
    def __init__(self, vars: list[Symbol], body: list[Expression], env: Environment):
        self.vars = vars
        self.body = body
        self.outer_env = env

    def env(self, args: list[Expression]) -> Environment:
        return Environment(dict(zip(self.vars, args)), self.outer_env)


type Atom = int | float | bool | String | Symbol | Procedure | Callable
type Expression = list[Expression] | Atom


class Environment:
    def __init__(self, frame: dict[Symbol, Expression] = {}, outer: Environment | None = None):
        self.frame = frame
        self.outer = outer

    def find(self, symbol: Symbol) -> Environment:
        return self if symbol in self.frame else self.outer.find(symbol)

    def get(self, symbol: Symbol) -> Expression:
        return self.find(symbol).frame[symbol]

    def define(self, symbol: Symbol, value: Expression) -> None:
        self.frame[symbol] = value

    def set(self, symbol: Symbol, value: Expression) -> None:
        self.find(symbol).frame[symbol] = value


modules = {
    "standard": {
        "1.0": {
            "print": print,
            "after": lambda delay, callback: root.after(delay, callback),
            "+": lambda *args: operator.add(*args) if len(args) > 1 else operator.pos(*args),
            "-": lambda *args: operator.sub(*args) if len(args) > 1 else operator.neg(*args),
            "*": operator.mul,
            "/": operator.truediv,
            "abs": operator.abs,
            "modulo": operator.mod,
            "expt": operator.pow,
            "=": operator.eq,
            "<": operator.lt,
            "<=": operator.le,
            ">": operator.gt,
            ">=": operator.ge,
            "not": operator.not_,
        },
    },
    "edgeware": {
        "1.0": {
            "image": lambda: ImagePopup(root, settings, pack, state),
            "video": lambda: VideoPopup(root, settings, pack, state),
            "subliminal": lambda: SubliminalMessagePopup(settings, pack),
            "notification": lambda: display_notification(settings, pack),
            "web": lambda: open_web(pack),
            "audio": lambda: play_audio(pack),
        },
    },
}


def tokenize(code: str) -> list[str]:
    chars = list(code)
    tokens = []
    while chars:
        char = chars.pop(0)
        token = char

        if char.isspace():
            continue
        elif char == ";":
            while chars[0] != "\n":
                chars.pop(0)
        elif char in ["(", ")", "'"]:
            tokens.append(token)
        elif char == '"':
            while chars[0] != '"':
                char = chars.pop(0)
                token += chars.pop(0) if char == "\\" else char
            token += chars.pop(0)
            tokens.append(token)
        else:
            while not (chars[0].isspace() or chars[0] in ["(", ")", ";"]):
                token += chars.pop(0)
            tokens.append(token)

    return ["("] + tokens + [")"]


def parse(tokens: list[str]) -> list[Expression]:
    token = tokens.pop(0)
    if token == "(":
        list = []
        while tokens[0] != ")":
            list.append(parse(tokens))
        tokens.pop(0)
        return list
    elif token == "'":
        return [Symbol("quote"), parse(tokens)]
    else:
        try:
            return int(token)
        except ValueError:
            pass

        try:
            return float(token)
        except ValueError:
            pass

        if token == "#t":
            return True
        elif token == "#f":
            return False
        elif token[0] == '"' and token[-1] == '"':
            return String(token[1:-1])
        else:
            return Symbol(token)


def eval(exp: Expression, env: Environment) -> Expression | None:
    while True:
        match exp:
            case int() | float() | bool() | String():
                return exp

            case Symbol():
                return env.get(exp)

            case [Symbol("quote"), *cdr]:
                assert len(cdr) == 1
                return cdr[0]

            case [Symbol("lambda"), *cdr]:
                assert len(cdr) >= 1
                vars, *body = cdr
                assert isinstance(vars, list) and all([isinstance(var, Symbol) for var in vars])
                return Procedure(vars, body, env)

            case [Symbol("if"), *cdr]:
                assert len(cdr) in [2, 3]
                test, consequent, *alternate = cdr
                if eval(test, env):
                    exp = consequent
                elif len(cdr) == 3:
                    exp = alternate[0]
                else:
                    return

            case [Symbol("define"), *cdr]:
                assert len(cdr) == 2
                var, value = cdr
                assert isinstance(var, Symbol)
                env.define(var, eval(value, env))
                return

            case [Symbol("set!"), *cdr]:
                assert len(cdr) == 2
                var, value = cdr
                assert isinstance(var, Symbol)
                env.set(var, eval(value, env))
                return

            case [Symbol("import"), *cdr]:
                assert all([isinstance(spec, list) and len(spec) == 2 and isinstance(spec[0], Symbol) and isinstance(spec[1], String) for spec in cdr])
                for spec in cdr:
                    module, version = spec
                    for var, value in modules[module][version].items():
                        env.define(var, value)
                return

            case [Symbol("and"), *cdr]:
                if len(cdr) > 0:
                    test = cdr.pop(0)
                    exp = [Symbol("if"), test, [Symbol("and"), *cdr], False]
                else:
                    exp = True

            case [Symbol("or"), *cdr]:
                if len(cdr) > 0:
                    test = cdr.pop(0)
                    exp = [Symbol("let"), [[Symbol("test"), test]], [Symbol("if"), Symbol("test"), Symbol("test"), [Symbol("or"), *cdr]]]
                else:
                    exp = False

            case [Symbol("let"), *cdr]:
                assert len(cdr) >= 1 and (isinstance(cdr[0], Symbol) or isinstance(cdr[0], list))
                if isinstance(cdr[0], Symbol):
                    # Named let
                    name, bindings, *body = cdr
                    assert isinstance(bindings, list) and all([len(binding) == 2 and isinstance(binding[0], Symbol) for binding in bindings])
                    vars = [var for var, init in bindings]
                    exp = [Symbol("let"), [*bindings, [name, [Symbol("lambda"), vars, *body]]], [name, *vars]]
                else:
                    # letrec*
                    bindings, *body = cdr
                    assert all([len(binding) == 2 and isinstance(binding[0], Symbol) for binding in bindings])
                    if len(bindings) > 0:
                        var, init = bindings.pop(0)
                        exp = [[Symbol("lambda"), [], [Symbol("define"), var, init], [Symbol("let"), bindings, *body]]]
                    else:
                        exp = [[Symbol("lambda"), [], *body]]

            case [Symbol("begin"), *cdr]:
                if len(cdr) > 1:
                    exp = [Symbol("if"), cdr.pop(0), [Symbol("begin"), *cdr], [Symbol("begin"), *cdr]]
                else:
                    exp = cdr[0]

            case [operator, *cdr]:
                procedure = eval(operator, env)
                args = [eval(arg, env) for arg in cdr]
                if isinstance(procedure, Procedure):
                    p_env = procedure.env(args)
                    for p_exp in procedure.body[0:-1]:
                        eval(p_exp, p_env)
                    exp, env = procedure.body[-1], p_env
                else:
                    return procedure(*args)

            case _:
                raise Exception(f"Syntax error in expression {exp}")


env = Environment()
for exp in parse(tokenize(script)):
    eval(exp, env)

root.after(1000, sys.exit)
root.mainloop()
