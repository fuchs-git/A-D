'''
Das ist eine Custom Liste, die sich so verhalten soll wie die buitin Liste
'''
from typing import Any


class Liste:
    def __init__(self):
        self.first = None

    def __repr__(self):
        if self.first is None:
            return '[]'
        return f'[{repr(self.first)}]'

    def __len__(self):
        if self.first is None:
            return 0
        return len(self.first)

    def append(self, value: Any):
        if self.first is None:
            self.first = Wagon(value)
        else:
            self.first.append(value)


class Wagon:
    def __init__(self, value: Any):
        self.next = None
        self.value = value

    def __repr__(self):
        if self.next is None:
            return f'{repr(self.value)}'
        return f'{repr(self.value)}, ' + repr(self.next)

    def __len__(self):
        if self.next is None:
            return 1
        return len(self.next) + 1

    def append(self, value):
        if self.next is None:
            self.next = Wagon(value)
        else:
            self.next.append(value)


liste = Liste()
print(len(liste))
liste.append(3)
print(liste)
liste.append(4)
print(len(liste))
liste.append(5)
print(len(liste))
print(liste)
