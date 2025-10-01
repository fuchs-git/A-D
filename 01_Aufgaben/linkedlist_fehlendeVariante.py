'''
Ihnen ist sicher nicht entgangen, dass wir bei der Rekursion in den Wagon zwei Varianten gesehen haben (eine mit Arbeit
 auf dem Hinweg, eine mit Arbeit auf dem Rückweg).

Natürlich gibt es auch bei der Rekursion in der Lok die Möglichkeit, die Arbeit bereits auf dem Hinweg zu verrichten.

Implementieren Sie diese noch fehlende Variante. (Insgesamt sollten Sie dann vier Varianten haben Lok+Hin, Lok+Rück, Wagon+Hin, Wagon+Rück).
'''

from typing import Any


class Liste:

    def __init__(self):
        self.first = None

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

    # Längenermittlung auf dem klassischen Weg
    def len_iterativ(self):
        if self.first is None:
            return 0
        else:
            schaffner = self.first
            length = 1
            while schaffner.next is not None:
                length += 1
                schaffner = schaffner.next
            return length

    def __len__(self) -> int:
        def len_rekursiv(wagon: Wagon) -> int:
            if wagon is None:
                return 0
            return len_rekursiv(wagon.next) + 1

        return len_rekursiv(self.first)

    def append(self, value: Any):
        neuer_wagon = Wagon(value)
        if self.first is None:
            self.first = neuer_wagon
            print(f'Neuer Wagon mit Value {value}')
        else:
            schaffner = self.first
            while schaffner.next is not None:
                schaffner = schaffner.next
            schaffner.next = neuer_wagon
            print(f'Weiterer Wagon mit Value {value}')


class Wagon:
    def __init__(self, value: Any):
        self.next = None
        self.value = value


# Tester
liste_meine = Liste()
liste_python = []

liste_meine.append(1)
liste_python.append(1)
liste_meine.append(2)
liste_python.append(2)
liste_meine.append("drei")
liste_python.append('drei')

print(f'{len(liste_meine)=}')
print(f'{len(liste_python)=}')
