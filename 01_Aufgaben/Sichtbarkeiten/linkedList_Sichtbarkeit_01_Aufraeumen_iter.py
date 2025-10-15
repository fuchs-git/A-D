'''
Das ist eine Custom Liste, die sich so verhalten soll wie die builtin Liste
'''
from typing import Any


class Liste:
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

        def append(self, value):
            if self.next is None:
                self.next = Liste._Wagon(value)
            else:
                self.next.append(value)

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

    def append(self, value: Any):
        if self._first is None:
            self._first = self._Wagon(value)
        else:
            self._first.append(value)

    def copy(self):
        kopie = Liste()
        if self._first is None:
            return kopie
        schaffner = self._first
        while schaffner is not None:
            kopie.append(schaffner.value)
            schaffner = schaffner.next
        return kopie


liste = Liste()
print(len(liste))
liste.append(3)
print(liste)
liste.append(4)
print(len(liste))
liste.append('drei')
print(liste)

a = [1, 2, 3]
b = a.copy()

c = Liste()
[c.append(i) for i in range(3)]
print(c)
d = c.copy()
print(d)
d.append(5)
print(d)
print(c)
print(type(d))
