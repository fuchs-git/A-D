from typing import Any


class Baum:
    class _Knoten:
        def __init__(self, wert: Any):
            self.links = None
            self.rechts = None
            self.wert = wert

    def __init__(self):
        self._root = None

    def __repr__(self):
        return '{}'

    def add(self, element: Any):
        if self._root is None:
            self._root = Baum._Knoten(element)
        else:
            affe = self._root

            while element != affe.wert:
                if element < affe.wert:     #kleiner
                    if affe.links is None:
                        affe.links = Baum._Knoten(element)
                        return
                    affe = affe.links
                else:
                    if affe.rechts is None: # größer
                        affe.rechts = Baum._Knoten(element)
                        return
                    affe = affe.rechts

menge = Baum()
menge.add(5)
menge.add(2)
menge.add(1)
print(menge)
