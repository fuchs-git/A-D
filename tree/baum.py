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

    def contains_entrek(self, item):
        todo = [self.wurzel]
        while todo:
            jetzt: Baum._Knoten
            jetzt = todo.pop()
            if jetzt.wert == item:
                return True

            if jetzt is not None:
                return False

            todo.append(jetzt.rechts)
            todo.append(jetzt.links)

    def __iter__(self):
        def rek(knoten: Baum._Knoten):
            if knoten is None:
                return
            yield from rek(knoten.links)
            yield knoten.wert
            yield from rek(knoten.rechts)

        yield from rek(self.wurzel)

    def __iter__entr(self):
        todo = [self.wurzel]
        while todo:
            akt: Baum._Knoten
            akt = todo.pop()
            if akt is not None:
                yield akt.wert
                todo.append(akt.links)
                todo.append(akt.rechts)

    def __len__(self):  # rekursiv
        def rek(knoten: Baum._Knoten):
            if knoten is None:
                return 0
            return rek(knoten.links) + 1 + rek(knoten.rechts)

        return rek(self.wurzel)

    def len_entrek(self):
        ergebnis = 0
        todo = [self.wurzel]
        while todo:
            jetzt: Baum._Knoten
            jetzt = todo.pop()
            if jetzt is not None:
                ergebnis += 1
                todo.append(jetzt.links)
                todo.append(jetzt.rechts)
        return ergebnis

    def __repr__(self):
        def list_tree(knoten: Baum._Knoten):
            if knoten is None:
                return ""
            result = list_tree(knoten.links)
            result = result + (", " if knoten.links is not None else "") + str(knoten.wert)
            result = result + (", " if knoten.rechts is not None else "") + list_tree(knoten.rechts)
            return result

        return "{" + list_tree(self.wurzel) + "}"

    def strrek(self):  # rekursiv
        def rek(knoten: Baum._Knoten):
            if knoten is None:
                return ""
            return f"{rek(knoten.links)}{knoten.wert}, {rek(knoten.rechts)}"

        return f"{{{rek(self.wurzel)[:-2]}}}"

    def __str__(self):  # entrekursiv
        ergebnis = ""
        todo = [self.wurzel]

        while todo:
            jetzt_machen: Baum._Knoten
            jetzt_machen = todo.pop()
            if jetzt_machen is not None:
                ergebnis += f'{jetzt_machen.wert}, '
                todo.append(jetzt_machen.links)
                todo.append(jetzt_machen.rechts)
        return f"{{{ergebnis[:-2]}}}"

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

    def add_rek(self, wert: Any):  # so kann der Baum entarten!
        if self.wurzel is None:
            self.wurzel = Baum._Knoten(wert)
            return True

        def rek(knoten: Baum._Knoten):
            if wert == knoten.wert:
                return
            elif wert < knoten.wert:
                if knoten.links is None:
                    knoten.links = Baum._Knoten(wert)
                else:
                    rek(knoten.links)
            else:
                if knoten.rechts is None:
                    knoten.rechts = Baum._Knoten(wert)
                else:
                    rek(knoten.rechts)

        return rek(self.wurzel)

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
# for e in (7, 3, 1, 0, 2, 5, 4, 6, 11, 9, 8, 10, 13, 12, 14):
for e in (1, 2, 0):
    menge.add(e)

for e in menge:
    print(e)

# print(menge.treeview1())
# print(menge.treeview2())
print(menge.__str__())
print(menge.len_entrek())
print(menge.contains_entrek(1))
