from typing import Any


class Baum:
    class _Knoten:
        def __init__(self, value: Any):
            self.links = None
            self.rechts = None
            self.value = value

    def __init__(self):
        self._root = None

    def __repr__(self):
        return '{}'

    def add(self, element: Any):
        ...