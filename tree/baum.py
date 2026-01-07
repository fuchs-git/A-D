from typing import Any


class Baum:  # könnte man auch "Menge" nennen oder "Set" oder "TreeSet"
    """
    Mengenimplementierung mit einem Binärbaum
    """

    class _Knoten:
        def __init__(self, wert: Any):
            self.wert = wert
            self.links = None
            self.rechts = None

    def __init__(self):
        self.wurzel = None


    def __contains__(self, item):
        def rek(knoten: Baum._Knoten):
            if knoten is None:
                return False
            if knoten.wert == item:
                return True
            return rek(knoten.links) if item < knoten.wert else rek(knoten.rechts)
        return rek(self.wurzel)

    def __iter__(self):
        def rek(knoten: Baum._Knoten):
            if knoten is None:
                return
            yield from rek(knoten.links)
            yield knoten.wert
            yield from rek(knoten.rechts)

        yield from rek(self.wurzel)

    def __len__(self):
        def rek(knoten: Baum._Knoten):
            if knoten is None:
                return 0
            return rek(knoten.links) + 1 + rek(knoten.rechts)
        return rek(self.wurzel)


    def __repr__(self):
        def list_tree(knoten: Baum._Knoten):
            if knoten is None:
                return ""
            result = list_tree(knoten.links)
            result = result + (", " if knoten.links is not None else "") + str(knoten.wert)
            result = result + (", " if knoten.rechts is not None else "") + list_tree(knoten.rechts)
            return result

        return "{" + list_tree(self.wurzel) + "}"

    def __str__(self):
        def rek(knoten: Baum._Knoten):
            if knoten is None:
                return ""
            return f"{rek(knoten.links)}{knoten.wert}, {rek(knoten.rechts)}"

        return f"{{{rek(self.wurzel)[:-2]}}}"

    def add(self, wert: Any):  # so kann der Baum entarten!
        if self.wurzel is None:
            self.wurzel = Baum._Knoten(wert)
        else:
            aktuell = self.wurzel
            while aktuell.wert != wert:
                if wert < aktuell.wert:
                    if aktuell.links is None:
                        aktuell.links = Baum._Knoten(wert)
                        return
                    aktuell = aktuell.links
                else:
                    if aktuell.rechts is None:
                        aktuell.rechts = Baum._Knoten(wert)
                        return
                    aktuell = aktuell.rechts

    def treeview1(self):
        def rek(knoten: Baum._Knoten, tiefe=0):
            if knoten is None:
                return ""
            return f"{rek(knoten.rechts, tiefe + 1)}{'\t' * tiefe}{knoten.wert}\n{rek(knoten.links, tiefe + 1)}"
        return rek(self.wurzel)
    def treeview2(self):
        def rek(knoten: Baum._Knoten, tiefe=0):
            if knoten is None:
                return ""
            return (f"{'    ' * (tiefe - 1)}{'└── ' if tiefe else ''}{knoten.wert}\n"
                    f"{rek(knoten.links, tiefe + 1)}"
                    f"{rek(knoten.rechts, tiefe + 1)}")
        return rek(self.wurzel)








menge = Baum()
for e in (7, 3, 1, 0, 2, 5, 4, 6, 11, 9, 8, 10, 13, 12, 14):
    menge.add(e)

for e in menge:
    print(e)

print(menge.treeview1())
print(menge.treeview2())