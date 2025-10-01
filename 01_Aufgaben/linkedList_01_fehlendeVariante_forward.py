from typing import Any


class Liste:

    def __init__(self):
        self.first = None

    # def __str__(self):
    #     return '[]'

    def __repr__(self):
        schaffner = self.first
        values = ''
        while schaffner is not None:
            if schaffner.value is not None:
                if values:
                    values += ', '
                values += repr(schaffner.value)
            schaffner = schaffner.next
        return f'[{values}]' if values else '[]'

    # ==================================================================
    # Länge wird im Wagon ermittelt
    # ==================================================================
    def __len__(self) -> int:
        if self.first is None:
            return 0
        return self.first.len_forward(1)

    def append(self, value: Any):
        neuer_wagon = Wagon(value)
        if self.first is None:
            self.first = neuer_wagon
            # print(f'Neuer Wagon mit Value {value}')
        else:
            schaffner = self.first
            while schaffner.next is not None:
                schaffner = schaffner.next
            schaffner.next = neuer_wagon
            # print(f'Weiterer Wagon mit Value {value}')


class Wagon:
    # ==================================================================
    # Forwärts ermittelt
    # __len__() akzeptiert nur ein Argument! daher len_forward
    # ==================================================================
    def len_forward(self, counter: int) -> int:
        if self.next is None:
            return counter
        return self.next.len_forward(counter + 1)

    def __init__(self, value: Any):
        self.next = None
        self.value = value


lst = Liste()
lst.append(1)
lst.append(2)
lst.append(3)
print(len(lst))