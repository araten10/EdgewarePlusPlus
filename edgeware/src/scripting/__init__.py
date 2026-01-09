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

# Lua 5.4 syntax: https://www.lua.org/manual/5.4/manual.html#9

import logging
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


class NameList(list[str]):
    def __init__(self, tokens: Tokens) -> None:
        super().__init__()
        self.append(tokens.get_name())
        while tokens.skip_if(","):
            self.append(tokens.get_name())


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


class TableConstructor:
    def __init__(self, tokens: Tokens) -> None:
        index = 1
        self.entries = []

        tokens.skip("{")
        while tokens.next != "}":
            if tokens.skip_if("["):
                key_exp = Expression(tokens)
                tokens.skip("]")
                tokens.skip("=")
                value_exp = Expression(tokens)
                self.entries.append((key_exp, value_exp))
            elif tokens.ahead == "=":
                name = tokens.get_name()
                tokens.skip("=")
                value_exp = Expression(tokens)
                self.entries.append((name, value_exp))
            else:
                value_exp = Expression(tokens)
                self.entries.append((index, value_exp))
                index += 1

            if tokens.next != "}" and not tokens.skip_if(","):
                tokens.skip(";")

        tokens.skip("}")

    def eval(self, env: Environment) -> dict:
        table = {}
        for key, value in self.entries:
            if isinstance(key, Expression):
                key = key.eval(env)
            table[key] = value.eval(env)

        return table


class Prefix:
    def __init__(self, tokens: Tokens) -> None:
        if tokens.skip_if("("):
            exp = Expression(tokens)
            tokens.skip(")")
            self.assign = None
            self.eval = exp.eval
        else:
            name = tokens.get_name()
            self.assign = lambda env, value, name=name: env.assign(name, value)
            self.eval = lambda env, name=name: env.get(name)  # noqa: E731

        while True:
            # Assign must be set before eval since it relies on the previous eval in the chain
            if tokens.skip_if("."):
                name = tokens.get_name()
                self.assign = lambda env, value, eval=self.eval, name=name: eval(env).update({name: value})
                self.eval = lambda env, eval=self.eval, name=name: eval(env)[name]  # noqa: E731
            elif tokens.skip_if("["):
                exp = Expression(tokens)
                tokens.skip("]")
                self.assign = lambda env, value, eval=self.eval, exp=exp: eval(env).update({exp.eval(env): value})
                self.eval = lambda env, eval=self.eval, exp=exp: eval(env)[exp.eval(env)]  # noqa: E731
            elif tokens.skip_if("("):
                args = []
                if not tokens.skip_if(")"):
                    args = ExpressionList(tokens)
                    tokens.skip(")")
                self.assign = None
                self.eval = lambda env, eval=self.eval: self.return_value(eval(env)(env, *[arg.eval(env) for arg in args]))  # noqa: E731
            elif tokens.next == "{":
                table = TableConstructor(tokens)
                self.assign = None
                self.eval = lambda env, eval=self.eval: self.return_value(eval(env)(env, table.eval(env)))  # noqa: E731
            elif tokens.next[0] == '"':
                string = PrimaryExpression(tokens)
                self.assign = None
                self.eval = lambda env, eval=self.eval: self.return_value(eval(env)(env, string.eval(env)))  # noqa: E731
            else:
                break

    def is_var(self) -> bool:
        return bool(self.assign)

    def return_value(self, value: ReturnValue | None) -> object | None:
        if isinstance(value, ReturnValue):
            return value.value


class PrimaryExpression:
    """Expression that does not contain operators"""

    def __init__(self, tokens: Tokens) -> None:
        constants = {"nil": None, "false": False, "true": True}

        if tokens.next in constants:
            value = constants[tokens.get()]
            self.eval = lambda _env: value

        elif tokens.next[0] == '"' and tokens.next[-1] == '"':
            string = tokens.get()
            self.eval = lambda _env: string[1:-1]

        elif tokens.next == "{":
            table = TableConstructor(tokens)
            self.eval = table.eval

        elif tokens.skip_if("function"):
            body = FunctionBody(tokens)
            self.eval = body.eval

        else:
            for numeral in [int, float]:
                try:
                    number = numeral(tokens.next)
                    tokens.skip()
                    self.eval = lambda _env: number
                    return
                except ValueError:
                    pass

            prefix = Prefix(tokens)
            self.eval = prefix.eval


class Expression:
    def __init__(self, tokens: Tokens) -> None:
        from scripting.operator import operator_eval

        self.eval = operator_eval(tokens)


class ExpressionList(list[Expression]):
    def __init__(self, tokens: Tokens) -> None:
        super().__init__()
        self.append(Expression(tokens))
        while tokens.skip_if(","):
            self.append(Expression(tokens))


class NilExpression:
    def eval(self, _env: Environment) -> None:
        return


class Statement:
    def __init__(self, tokens: Tokens) -> None:
        match tokens.next:
            case ";":
                tokens.skip(";")
                self.eval = lambda _env: None

            case "do":
                tokens.skip("do")
                block = Block(tokens, "end")
                self.eval = lambda env: block.eval(env)

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

            case "function":
                tokens.skip("function")
                name = tokens.get_name()
                body = FunctionBody(tokens)
                self.eval = lambda env: env.assign(name, body.eval(env))

            case "local":
                tokens.skip("local")
                if tokens.skip_if("function"):
                    name = tokens.get_name()
                    body = FunctionBody(tokens)

                    def local_function_eval(env: Environment) -> None:
                        env.define(name, None)
                        env.assign(name, body.eval(env))

                    self.eval = local_function_eval
                else:
                    name = tokens.get_name()
                    tokens.skip("=")
                    value = Expression(tokens)
                    self.eval = lambda env: env.define(name, value.eval(env))

            case _:
                prefix = Prefix(tokens)
                if prefix.is_var():
                    vars = [prefix]
                    while tokens.skip_if(","):
                        prefix = Prefix(tokens)
                        vars.append(prefix)
                    tokens.skip("=")
                    values = ExpressionList(tokens)

                    def assign_eval(env: Environment) -> None:
                        for i, var in enumerate(vars):
                            value = values[i] if len(values) > i else NilExpression()
                            var.assign(env, value.eval(env))

                    self.eval = assign_eval
                else:
                    # Function call
                    self.eval = prefix.eval


class Block:
    """List of statements executed sequentially with an optional final return statement"""

    def __init__(self, tokens: Tokens, terminate: str | list[str]) -> None:
        self.statements = []
        self.return_exp = None

        # Possible tokens that may terminate the block, transform to a list if
        # only one possibility is provided
        terminate_list = terminate if isinstance(terminate, list) else [terminate]

        while tokens.next not in terminate_list + ["return"]:
            self.statements.append(Statement(tokens))

        if tokens.skip_if("return"):
            self.return_exp = Expression(tokens) if tokens.next not in terminate_list else NilExpression()

        # Don't skip the terminating token if multiple possibilities are
        # provided. The caller needs to know which token terminated the block
        # and will handle it accordingly.
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
