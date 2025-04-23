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
