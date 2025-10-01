# Copyright (C) 2025 Araten & Marigold
#
# This file is part of Edgeware++.
#
# Edgeware++ is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Edgeware++ is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Edgeware++.  If not, see <https://www.gnu.org/licenses/>.

import logging
import operator
from dataclasses import dataclass
from tkinter import Tk
from typing import Callable

from config.settings import Settings
from pack import Pack
from state import State

from scripting.environment import Environment
from scripting.error import LuaError
from scripting.modules import get_modules
from scripting.tokens import Tokens

UN_OPS = {"-": operator.neg, "#": len, "not": operator.not_}
UN_PREC = 10

BINARY = {
    "+": (operator.add, 8, False),
    "-": (operator.sub, 8, False),
    "*": (operator.mul, 9, False),
    "/": (operator.truediv, 9, False),
    "//": (operator.floordiv, 9, False),
    "^": (operator.pow, 11, True),
    "%": (operator.mod, 9, False),
    "..": (operator.concat, 7, True),
    "<": (operator.lt, 2, False),
    "<=": (operator.le, 2, False),
    ">": (operator.gt, 2, False),
    ">=": (operator.ge, 2, False),
    "==": (operator.eq, 2, False),
    "~=": (operator.ne, 2, False),
    "and": (operator.and_, 1, False),
    "or": (operator.or_, 0, False),
}

BIN_OPS = {token: data[0] for token, data in BINARY.items()}
BIN_PREC = {token: data[1] for token, data in BINARY.items()}
RIGHT_ASSOC = {token: data[2] for token, data in BINARY.items()}


def identity(value: object) -> object:
    return value


class NameList(list[str]):
    def __init__(self, tokens: Tokens) -> None:
        super().__init__()
        self.append(tokens.get_name())
        while tokens.skip_if(","):
            self.append(tokens.get_name())


class Expression:
    pass


class ExpressionList(list[Expression]):
    def __init__(self, tokens: Tokens) -> None:
        super().__init__()
        self.append(Expression(tokens))
        while tokens.skip_if(","):
            self.append(Expression(tokens))


@dataclass
class ReturnValue:
    value: object


class FunctionBody:
    def __init__(self, tokens: Tokens) -> None:
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

        return lambda env, *args: self.block.eval(Environment(dict(zip(self.params, args)), env, closure))


class FunctionCall:
    def __init__(self, tokens: Tokens) -> None:
        self.name = tokens.get_name()
        tokens.skip("(")
        self.args = []
        if not tokens.skip_if(")"):
            self.args = ExpressionList(tokens)
            tokens.skip(")")

    def eval(self, env: Environment) -> object:
        # TODO: Adjustment https://www.lua.org/manual/5.4/manual.html#3.4.12
        value = env.get(self.name)(env, *[arg.eval(env) for arg in self.args])
        if isinstance(value, ReturnValue):
            return value.value


class PrimaryExpression:
    def __init__(self, tokens: Tokens) -> None:
        constants = {"nil": None, "false": False, "true": True}
        if tokens.next in constants:
            value = constants[tokens.get()]
            self.eval = lambda _env: value
            return

        for numeral in [int, float]:
            try:
                number = numeral(tokens.next)
                tokens.skip()
                self.eval = lambda _env: number
                return
            except ValueError:
                pass

        if tokens.next[0] == '"' and tokens.next[-1] == '"':
            string = tokens.get()
            self.eval = lambda _env: string[1:-1]
            return

        if tokens.skip_if("function"):
            body = FunctionBody(tokens)
            self.eval = lambda env: body.eval(env)
            return

        if tokens.skip_if("("):
            exp = Expression(tokens)
            tokens.skip(")")
            self.eval = exp.eval
            return

        if tokens.ahead == "(":
            call = FunctionCall(tokens)
            self.eval = lambda env: call.eval(env)
            return

        name = tokens.get_name()
        self.eval = lambda env: env.get(name)


class Expression:
    def __init__(self, tokens: Tokens) -> None:
        l_un = self.unary(tokens)
        left = PrimaryExpression(tokens)
        self.eval = self.binary(tokens, l_un, left.eval)

    # Modified version of the precedence climbing algorithm from Wikipedia
    # https://en.wikipedia.org/wiki/Operator-precedence_parser#Pseudocode
    def binary(self, tokens: Tokens, l_un: Callable, l_eval: Callable, min_precedence: int = 0) -> Callable:
        while tokens.next in BIN_OPS and (BIN_PREC[tokens.next] >= min_precedence):
            token = tokens.get()
            op = BIN_OPS[token]
            prec = BIN_PREC[token]

            r_un = self.unary(tokens)
            right = PrimaryExpression(tokens)
            r_eval = right.eval
            while tokens.next in BIN_OPS and ((BIN_PREC[tokens.next] > prec) or ((BIN_PREC[tokens.next] == prec) and RIGHT_ASSOC[tokens.next])):
                r_eval = self.binary(tokens, r_un, right.eval, prec + (1 if BIN_PREC[tokens.next] > prec else 0))
                r_un = identity

            l_eval = lambda env, lu=l_un, le=l_eval, op=op, prec=prec, ru=r_un, re=r_eval: (  # noqa: E731
                lu(op(le(env), ru(re(env)))) if prec > UN_PREC else op(lu(le(env)), ru(re(env)))
            )
            l_un = identity

        return lambda env: l_un(l_eval(env))

    def unary(self, tokens: Tokens) -> Callable:
        chain = identity
        while tokens.next in UN_OPS:
            op = UN_OPS[tokens.get()]
            chain = lambda value, chain=chain, op=op: chain(op(value))  # noqa: E731
        return chain


class Statement:
    def __init__(self, tokens: Tokens) -> None:
        match tokens.next:
            case "do":
                tokens.skip("do")
                block = Block(tokens, "end")
                self.eval = lambda env: block.eval(env)
                return
            case "while":
                tokens.skip("while")
                while_exp = Expression(tokens)
                tokens.skip("do")
                block = Block(tokens, "end")

                def while_eval(env: Environment) -> ReturnValue | None:
                    while while_exp.eval(env):
                        value = block.eval(env)
                        if isinstance(value, ReturnValue):
                            return value

                self.eval = while_eval
                return
            case "if":
                tokens.skip("if")
                if_exp = Expression(tokens)
                tokens.skip("then")
                then_block = Block(tokens, ["elseif", "else", "end"])

                chain = [(if_exp, then_block)]

                while tokens.skip_if("elseif"):
                    elseif_exp = Expression(tokens)
                    tokens.skip("then")
                    elseif_block = Block(tokens, ["elseif", "else", "end"])
                    chain.append((elseif_exp, elseif_block))

                if tokens.skip_if("else"):
                    else_block = Block(tokens, "end")
                    chain.append(else_block)
                else:
                    tokens.skip("end")

                def if_eval(env: Environment) -> ReturnValue | None:
                    for branch in chain:
                        if isinstance(branch, tuple):
                            exp, block = branch
                            if exp.eval(env):
                                return block.eval(env)
                        else:
                            block = branch
                            return block.eval(env)

                self.eval = if_eval
                return
            case "function":
                tokens.skip("function")
                name = tokens.get_name()
                body = FunctionBody(tokens)
                self.eval = lambda env: env.assign(name, body.eval(env))
                return
            case "local":
                tokens.skip("local")
                if tokens.skip_if("function"):
                    name = tokens.get_name()
                    body = FunctionBody(tokens)

                    def local_function_eval(env: Environment) -> None:
                        env.define(name, None)
                        env.assign(name, body.eval(env))

                    self.eval = local_function_eval
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
    def eval(self, _env: Environment) -> None:
        return


class Block:
    def __init__(self, tokens: Tokens, terminate: str | list[str]) -> None:
        self.statements = []
        self.return_exp = None
        terminate_list = terminate if isinstance(terminate, list) else [terminate]

        while tokens.next not in terminate_list + ["return"]:
            self.statements.append(Statement(tokens))

        if tokens.skip_if("return"):
            self.return_exp = Expression(tokens) if tokens.next not in terminate_list else ReturnExpression()

        if not isinstance(terminate, list):
            tokens.skip(terminate)

    def eval(self, external: Environment) -> ReturnValue | None:
        env = Environment({}, external)
        for statement in self.statements:
            value = statement.eval(env)
            if isinstance(value, ReturnValue):
                return value

        if self.return_exp is not None:
            return ReturnValue(self.return_exp.eval(env))


def run_script(root: Tk, settings: Settings, pack: Pack, state: State) -> None:
    if not pack.paths.script.is_file():
        return

    modules = get_modules(root, settings, pack, state)

    def require(env: Environment, module: str) -> None:
        for name, value in modules[module].items():
            env.assign(name, value)

    env = Environment({"require": require})

    with open(pack.paths.script, "r") as f:
        script = f.read()

    try:
        tokens = Tokens(script)
        block = Block(tokens, "end")
        block.eval(env)
    except LuaError as e:
        logging.error(f"Lua error: {e}")
