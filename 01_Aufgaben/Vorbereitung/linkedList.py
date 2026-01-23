from typing import Any


class Liste:
    class _Element:
        def __init__(self, value: Any):
            self.next = None
            self.value = value

        def __repr__(self):  # rekursiv
            if self.next is None:
                return f'{repr(self.value)}'
            else:
                return f'{repr(self.value)}, {repr(self.next)}'

        def append(self, value):
            if self.next is None:
                self.next = Liste._Element(value)
            else:
                self.next.append(value)

    def __init__(self):
        self._first = None

    def __repr__(self):  # rekursiv
        if self._first is None:
            return f'[]'
        return f'[{self._first}]'

    def __str__(self):  # nicht rekursiv
        if self._first is None:
            return '[]'
        else:
            ergebnis = ''
            todo = [self._first]

            while todo:
                now: Liste._Element
                now = todo.pop()
                if now is not None:
                    ergebnis += f'{now.value}, '
                    todo.append(now.next)
        return f'[{ergebnis[:-2]}]'

    def add(self, value: Any):
        if self._first is None:
            self._first = Liste._Element(value)
        else:
            self._first.append(value)

    def __len__(self):
        def rek(value: Liste._Element):
            if value is None:
                return 0
            return rek(value.next) +1

        return rek(self._first)


meineListe = Liste()
meineListe.add(5)
meineListe.add(4)
meineListe.add(3)
print(meineListe)
print(meineListe.__str__())

print(len(meineListe))
