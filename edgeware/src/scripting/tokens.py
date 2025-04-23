from collections.abc import Iterable

KEYWORDS = [
    "and",
    "break",
    "do",
    "else",
    "elseif",
    "end",
    "false",
    "for",
    "function",
    "goto",
    "if",
    "in",
    "local",
    "nil",
    "not",
    "or",
    "repeat",
    "return",
    "then",
    "true",
    "until",
    "while",
]

SPECIAL_TOKENS = [
    "...",
    "<<",
    ">>",
    "//",
    "==",
    "~=",
    "<=",
    ">=",
    "::",
    "..",
    "+",
    "-",
    "*",
    "/",
    "%",
    "^",
    "#",
    "&",
    "~",
    "|",
    "<",
    ">",
    "=",
    "(",
    ")",
    "{",
    "}",
    "[",
    "]",
    ";",
    ":",
    ",",
    ".",
]

ESCAPE_SEQUENCES = {
    "a": "\a",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "v": "\v",
    "\\": "\\",
    '"': '"',
}


class Chars(list[str]):
    def __init__(self, code: str):
        super().__init__(list(code))

    def get(self) -> str:
        return self.pop(0)

    def delete(self, n: int = 1) -> None:
        del self[0:n]

    def starts_with(self, prefix: str) -> bool:
        return self[0 : len(prefix)] == list(prefix)

    def starts_with_any(self, prefixes: Iterable[str]) -> str | None:
        return next((prefix for prefix in prefixes if self.starts_with(prefix)), None)


class Tokens(list[str]):
    def __init__(self, code: str):
        super().__init__()
        chars = Chars(code)

        while chars:
            if chars.starts_with("--"):
                terminate = "]]" if chars.starts_with("--[[") else "\n"
                while not chars.starts_with(terminate):
                    chars.delete()
                chars.delete(len(terminate))
                continue

            if chars[0].isspace():
                chars.delete()
                continue

            token = chars.starts_with_any(SPECIAL_TOKENS)
            if token:
                self.append(token)
                chars.delete(len(token))
                continue

            if chars[0] == '"':
                token = chars.get()
                while chars[0] != '"':
                    char = chars.get()
                    match char:
                        case "\\":
                            if not chars.starts_with_any(ESCAPE_SEQUENCES):
                                raise Exception(f"Invalid escape sequence \\{chars[0]}")
                            token += ESCAPE_SEQUENCES[chars.get()]
                        case "\n":
                            raise Exception("Unescaped line break in short literal string")
                        case _:
                            token += char
                token += chars.get()
                self.append(token)
                continue

            token = chars.get()
            delimiter = lambda: chars.starts_with("--") or chars[0].isspace() or chars.starts_with_any(SPECIAL_TOKENS) or chars[0] == '"'  # noqa: E731
            fraction = lambda: chars.starts_with_any(SPECIAL_TOKENS) == "." and token[0].isdigit()  # noqa: E731
            while not delimiter() or fraction():
                token += chars.get()
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
        if not all([char.isalnum() or char == "_" for char in self.next]) or self.next[0].isdigit() or self.next in KEYWORDS:
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
