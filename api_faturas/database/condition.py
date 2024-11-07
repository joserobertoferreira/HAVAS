from typing import Any


class Condition:
    def __init__(self, operator: str, value: Any):
        self.operator = operator
        self.value = value

    def __repr__(self) -> str:
        return f'Condition(operator={self.operator}, value={self.value})'
