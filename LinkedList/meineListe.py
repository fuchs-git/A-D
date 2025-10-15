'''
Das ist eine Custom Liste, die sich so verhalten soll wie die builtin Liste
'''
from typing import Any


class Liste:
    class _Iterator:
        def __init__(self, first: Any):
            self.temp = first

        def __next__(self) -> Any:
            if self.temp is not None:
                v = self.temp.value
                self.temp = self.temp.next
                return v
            raise StopIteration

    class _Wagon:
        def __init__(self, value: Any):
            self.next = None
            self.value = value

        def __repr__(self):
            if self.next is None:
                return f'{repr(self.value)}'
            return f'{repr(self.value)}, {repr(self.next)}'

        def __len__(self):
            if self.next is None:
                return 1
            return len(self.next) + 1

        def __getitem__(self, index: int) -> Any:
            if index == 0:
                return self.value
            return self.next.__getitem__(index - 1)

        def append(self, value):
            if self.next is None:
                self.next = Liste._Wagon(value)
            else:
                self.next.append(value)

        def clone(self):
            kopie = Liste._Wagon(self.value)
            if self.next is not None:
                kopie.next = self.next.clone()
            return kopie

    def __init__(self):
        self._first = None

    def __repr__(self):
        if self._first is None:
            return '[]'
        return f'[{self._first}]'

    def __len__(self):
        if self._first is None:
            return 0
        return len(self._first)

    def __iter__(self):
        return self._Iterator(self._first)

    def __getitem__(self, index: int) -> Any:
        if self._first is None or index < 0 or index >= len(self):
            raise IndexError("list index out of range")
        else:
            return self._first.__getitem__(index)

    def append(self, value: Any):
        if self._first is None:
            self._first = Liste._Wagon(value)
        else:
            self._first.append(value)

    def copy(self):
        neu = Liste()
        if self._first is not None:
            neu._first = self._first.clone()
        return neu
