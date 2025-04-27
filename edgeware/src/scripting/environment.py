from typing import Any


class Environment:
    pass


class Environment:
    def __init__(self, scope: dict[str, Any], external: Environment | None = None, closure: set[str] | None = None) -> None:
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
