from typing import Any


class Condition:
    def __init__(self, operator: str, value: Any):
        self.operator = operator
        self.value = value

    def __repr__(self) -> str:
        return f'Condition(operator={self.operator}, value={self.value})'

    def __iter__(self):
        yield self.operator
        yield self.value

    def __getitem__(self, index):
        return (self.operator, self.value)[index]

    def __len__(self):
        return 2

    def as_tuple(self):
        return self.operator, self.value
