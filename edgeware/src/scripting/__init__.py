import operator
from dataclasses import dataclass
from typing import Any, Callable

from scripting.environment import Environment
from scripting.tokens import Tokens

# stat ::= break |
#          if exp then block {elseif exp then block} [else block] end |
#          for Name ‘=’ exp ‘,’ exp [‘,’ exp] do block end |
#          for parse_name_list in parse_expression_list do block end |

# binop ::= ‘..’

# unop ::= ‘#’


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
            case "do":
                tokens.skip("do")
                block = Block(tokens, "end")
                self.eval = lambda env: block.eval(env)
                return
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


script = """
function hello()
  print("Hello", world)
end

world = "world!"
hello()
"""


def run_script() -> None:
    env = Environment({"print": lambda *args: print(*args)})
    tokens = Tokens(script)
    block = Block(tokens, "end")
    block.eval(env)
