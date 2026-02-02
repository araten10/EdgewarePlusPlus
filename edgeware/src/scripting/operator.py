# Copyright (C) 2026 Araten & Marigold
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

import operator
from typing import Callable

from scripting import PrimaryExpression
from scripting.tokens import Tokens
from scripting.types import EvalFunction, LuaValue

type UnaryFunction = Callable[[LuaValue], LuaValue]

UN_OPS = {"-": operator.neg, "not": operator.not_, "#": len, "~": operator.inv}
UN_PREC = 10

# Define for each binary operator:
#  0: Implementation function
#  1: Precedence
#  2: Right associativity
BINARY = {
    "+": (operator.add, 8, False),
    "-": (operator.sub, 8, False),
    "*": (operator.mul, 9, False),
    "/": (operator.truediv, 9, False),
    "//": (operator.floordiv, 9, False),
    "^": (operator.pow, 11, True),
    "%": (operator.mod, 9, False),
    "&": (operator.and_, 5, False),
    "~": (operator.xor, 4, False),
    "|": (operator.or_, 3, False),
    ">>": (operator.rshift, 6, False),
    "<<": (operator.lshift, 6, False),
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


def identity(value: LuaValue) -> LuaValue:
    return value


def unary_apply(tokens: Tokens) -> UnaryFunction:
    """Returns a function to apply a list of unary operators"""
    chain = identity
    while tokens.next in UN_OPS:
        op = UN_OPS[tokens.get()]
        chain = lambda value, chain=chain, op=op: chain(op(value))  # noqa: E731
    return chain


# Modified version of the precedence climbing algorithm from Wikipedia
# https://en.wikipedia.org/wiki/Operator-precedence_parser#Pseudocode
def binary_eval(tokens: Tokens, l_un: UnaryFunction, l_eval: EvalFunction, min_precedence: int = 0) -> EvalFunction:
    while tokens.next in BIN_OPS and (BIN_PREC[tokens.next] >= min_precedence):
        token = tokens.get()
        op = BIN_OPS[token]
        prec = BIN_PREC[token]

        r_un = unary_apply(tokens)
        right = PrimaryExpression(tokens)
        r_eval = right.eval
        while tokens.next in BIN_OPS and ((BIN_PREC[tokens.next] > prec) or ((BIN_PREC[tokens.next] == prec) and RIGHT_ASSOC[tokens.next])):
            r_eval = binary_eval(tokens, r_un, right.eval, prec + (1 if BIN_PREC[tokens.next] > prec else 0))
            r_un = identity

        l_eval = lambda env, lu=l_un, le=l_eval, op=op, prec=prec, ru=r_un, re=r_eval: (  # noqa: E731
            lu(op(le(env), ru(re(env)))) if prec > UN_PREC else op(lu(le(env)), ru(re(env)))
        )
        l_un = identity

    return lambda env: l_un(l_eval(env))


def operator_eval(tokens: Tokens) -> EvalFunction:
    l_un = unary_apply(tokens)
    left = PrimaryExpression(tokens)
    return binary_eval(tokens, l_un, left.eval)
