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

    def len_normal(self):
        if self.first is None:
            return 0
        else:
            schaffner = self.first
            length = 1
            while schaffner.next is not None:
                length += 1
                schaffner = schaffner.next
            return length


    # ==================================================================
    # Länge wird im Wagon ermittelt
    # ==================================================================
    def __len__(self) -> int:
        if self.first is None:
            return 0
        return len(self.first)



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
    # Rückwärts ermittelt
    # ==================================================================
    def __len__(self):
        if self.next is None:
            return 1
        return len(self.next) + 1



    def __init__(self, value: Any):
        self.next = None
        self.value = value

