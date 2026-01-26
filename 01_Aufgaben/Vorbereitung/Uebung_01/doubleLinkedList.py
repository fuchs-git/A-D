from typing import Any

class DoubleLinked:
    class _Wagon:
        def __init__(self, value):
            self.next = None
            self.value = value
            self.prev = None

        def __repr__(self):
            return repr(self.value)

    # ab hier die Listeninterna

    def __init__(self):
        self._first = None

    def __contains__(self, item):  # nativer Support für den "in"-Operator (ohne Fallback auf iter oder getitem)
        for elem in self:
            if elem == item:
                return True
        return False

    def __iter__(self):  # Generator-Methode, nativer Support von Iteration via iter/next (ohne Fallback auf getitem)
        wagon = self._first
        while wagon is not None:
            yield wagon.value
            wagon = wagon.next

    def __getitem__(self, index) -> Any:  # indizierter Zugriff
        if type(index) is not int:
            raise TypeError("Index muss ein int sein")
        if index < 0 or self._first is None:  # index negativ oder Liste leer
            raise IndexError("list index out of range")  # das ist die kopierte Meldung der Python-Liste

        schaffner = self._first
        while index > 0:
            schaffner = schaffner.next
            if schaffner is None:
                raise IndexError("list index out of range")
            index -= 1
        return schaffner.value

    def __len__(self) -> int:  # len
        if self._first is None:
            return 0
        else:
            schaffner = self._first
            counter = 1
            while schaffner.next is not None:
                schaffner = schaffner.next
                counter += 1
            return counter

    def __repr__(self) -> str:  # repr und str
        if self._first is None:
            return "[]"
        ergebnis = repr(self._first)
        schaffner = self._first
        while schaffner.next is not None:
            schaffner = schaffner.next
            ergebnis += f", {repr(schaffner)}"
        return f"[{ergebnis}]"

    def append(self, value: Any):
        if self._first is None:
            self._first = DoubleLinked._Wagon(value)
        else:
            schaffner = self._first
            while schaffner.next is not None:
                schaffner = schaffner.next
            neu = DoubleLinked._Wagon(value)
            schaffner.next = neu
            neu.prev = schaffner

    def insert(self, index: int, value: Any):

        if self._first is None:
            self.first = DoubleLinked._Wagon(value)
            return

        prev = self._first
        wagon = prev.next

        if index == 0:
            new_wagon = DoubleLinked._Wagon(value)
            self._first.prev = new_wagon
            new_wagon.next = self._first
            self._first = new_wagon
            return

        counter = 1
        while wagon is not None:
            print(wagon.value)
            if counter == index:
                new_wagon = DoubleLinked._Wagon(value)
                wagon.prev = new_wagon

                new_wagon.next = wagon
                new_wagon.prev = prev

                prev.next = new_wagon
                return

            counter += 1
            prev = prev.next
            wagon = wagon.next
        # Index out of Range? -> Wird am Ende angehangen
        prev.next = DoubleLinked._Wagon(value)

    def copy(self):  # Version ohne append
        kopie = DoubleLinked()
        schaffner_original = self._first
        if schaffner_original is not None:  # den ersten Wagen an die neue Lok hängen
            kopie._first = DoubleLinked._Wagon(schaffner_original.value)
            schaffner_kopie = kopie._first
            schaffner_original = schaffner_original.next
            while schaffner_original is not None:  # alle weiteren Wagen anhängen
                schaffner_kopie.next = DoubleLinked._Wagon(
                    schaffner_original.value)  # value wird nur "shallow" kopiert, nicht "deep"
                schaffner_kopie = schaffner_kopie.next
                schaffner_original = schaffner_original.next
        return kopie

    def unique(self):
        """
        ©️Beesten
        in-place, entfernt doppelt auftretende Elemente
        :return: nichts, es wird dir originale Liste (self) verändert
        """
        schaffner = self._first
        while schaffner is not None:
            vorgaenger = schaffner
            kontroletti = schaffner.next
            while kontroletti is not None:
                nachfolger = kontroletti.next
                if kontroletti.value == schaffner.value:
                    vorgaenger.next = nachfolger
                else:
                    vorgaenger = kontroletti
                kontroletti = nachfolger
            schaffner = schaffner.next
        return


liste = DoubleLinked()
liste.append(1)
liste.insert(0,0)

print(liste)