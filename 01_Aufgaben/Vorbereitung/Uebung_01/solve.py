from typing import Any


class Sequenz:
    class _Element:
        def __init__(self, value: Any):
            self.next = None
            self.value = value

        def __repr__(self):
            if self.next is None:
                return f'{repr(self.value)}'
            else:
                return f'{repr(self.value)}, {repr(self.next)}'

        def append(self, value: Any):
            if self.next is None:
                self.next = Sequenz._Element(value)
            else:
                self.next.append(value)

    def __init__(self):
        self.first = None

    def __repr__(self):
        if self.first is None:
            return '[]'
        return f'[{self.first}]'

    def __str__(self):  # nicht rekursiv
        if self.first is None:
            return '[]'
        else:
            ergebnis = ''
            todo = [self.first]

            while todo:
                now: Sequenz._Element
                now = todo.pop()
                if now is not None:
                    ergebnis += f'{now.value}, '
                    todo.append(now.next)
        return f'[{ergebnis[:-2]}]'

    def __iter__(self):
        """
        Macht die Sequenz iterierbar.
        Wir laufen mit einer Laufvariable (current) die next-Kette entlang
        und liefern nacheinander die gespeicherten Werte.
        """
        now: Sequenz._Element
        now = self.first
        while now is not None:
            yield now.value
            now = now.next

    def add(self, value: Any):
        if self.first is None:
            self.first = Sequenz._Element(value)
        else:
            self.first.append(value)

    def __len__(self):
        def rek(value: Sequenz._Element):
            if value is None:
                return 0
            return rek(value.next) + 1

        return rek(self.first)

    def len_entrekursiv(self):
        summe = 0
        todo = [self.first]

        while todo:
            now: Sequenz._Element
            now = todo.pop()
            if now is not None:
                summe += 1
                todo.append(now.next)
        return summe

    def sorted_copy(self):
        # 1) Arbeitskopie erstellen, damit self unverändert bleibt
        work = Sequenz()
        for value in self:
            work.add(value)

        # 2) Ergebnis-Sequenz (hier bauen wir die sortierte Kopie auf)
        result = Sequenz()

        # 3) Selection Sort: solange work noch Elemente hat
        while work.first is not None:

            # -------------------------
            # Minimum finden
            # -------------------------
            min_value = None
            todo = [work.first]

            while todo:
                now = todo.pop()

                # None ist KEIN Element -> sofort überspringen
                if now is None:
                    continue

                # Erstes echtes Element setzt min_value
                if min_value is None:
                    min_value = now.value
                # Danach normal vergleichen
                elif now.value < min_value:
                    min_value = now.value

                # Nur bei echten Elementen darf man now.next anhängen
                todo.append(now.next)

            # -------------------------
            # Pro Schleifendurchlauf ein Element nach result
            # -------------------------

            # Sonderfall: Minimum steht vorne
            if work.first.value == min_value:
                work.first = work.first.next
            else:
                prev = work.first
                current = work.first.next

                while current is not None:
                    if current.value == min_value:
                        # current "ausklinken": prev zeigt direkt auf current.next
                        prev.next = current.next
                        break
                    prev = current
                    current = current.next

            # -------------------------
            # Minimum ins Ergebnis übernehmen
            # -------------------------
            result.add(min_value)

        return result

    def stalin_sort_inplace(self):
        if self.first is None:
            return

        letzter_wert = self.first.value     # letzter wert
        prev = self.first                   # Vorgänger
        current = self.first.next           # aktuelles Element

        while current is not None:
            if current.value > letzter_wert:            # current bleibt, letzter-wert wird aktualisiert
                letzter_wert = current.value
                prev = current
            else:
                '''
                prev        current
                 ↓           ↓
                [7]  ---->  [3]  ---->  [1]  ---->  [6]
                '''
                prev.next = current.next
                '''
                [7]  ----------------->  [1]  ---->  [6]
                '''
                current = prev.next
                '''
                prev        current
                 ↓           ↓
                [7]  ---->  [1]  ---->  [6]
                '''


meineListe = Sequenz()
[meineListe.add(x) for x in [1,7,43,768,342,45645,653,21,7,2]]
# print(meineListe.len_entrekursiv())
# print(meineListe.sorted_copy())
print(meineListe)
meineListe.stalin_sort_inplace()
print(meineListe)
