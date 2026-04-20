import canvas_graph as cg


class Graph(cg.Graph):
    def __init__(self, **kwargs):
        cg.Graph.__init__(self, **kwargs)
        self.algo_hinzufuegen("Anzahl Knoten ausgeben", self.anzahl_knoten_ausgeben)
        self.algo_hinzufuegen("Anzahl Kanten ausgeben", self.anzahl_kanten_ausgeben)
        self.algo_hinzufuegen("alle Knoten iterieren", self.markiere_knoten)
        self.algo_hinzufuegen("alle Kanten iterieren", self.markiere_kanten)
        self.algo_hinzufuegen("alle Knoten stufenweise", self.markiere_kanten)
        self.algo_hinzufuegen("Breitensuche (BFS)", self.breitensuche)
        self.algo_hinzufuegen('Tiefensuche (DFS)', self.tiefensuche)
        self.algo_hinzufuegen("Zielsuche (BFS)", self.breitensuche_mit_ziel)
        self.algo_hinzufuegen("kreisfrei (BFS)", self.kreisfreiheit)
        self.algo_hinzufuegen('Zusammenhang (BFS)', self.ist_zusammenhaengend)
        self.algo_hinzufuegen('Anzahl ZHK', self.anzhal_zhk)
    #####################################  helper ################################
    def hole_nachbarknoten(self, kn: cg.Knoten):
        for ka in self.kanten:
            if ka.von is kn:
                yield ka.nach
            elif ka.nach is kn:
                yield ka.von

    def alle_knoten_aus(self):
        for kn in self.knoten:
            self.knoten_design(kn,
                               form=cg.FORM_KNOTEN,
                               rand=cg.FARBE_KNOTEN_RAND,
                               mitte=cg.FARBE_KNOTEN_MITTE)

    ################################### algos #####################################

    def anzahl_knoten_ausgeben(self):
        yield f"der Graph hat {len(self.knoten)} Knoten", False

    def anzahl_kanten_ausgeben(self):
        yield f"der Graph hat {len(self.kanten)} Kanten", False

    def markiere_knoten(self):
        self.alle_knoten_aus()
        for kn in self.knoten:
            self.knoten_design(kn, form=-5, rand="orange")
            yield f"Knoten {kn} markiert"
            self.knoten_design(kn, form=cg.FORM_KNOTEN, rand=cg.FARBE_KNOTEN_RAND)
        yield "fertig", False

    def markiere_kanten(self):
        for ka in self.kanten:
            self.kanten_design(ka, farbe="blue", striche=(10, 8))
            yield f"Kante {ka} markiert"
            self.kanten_design(ka, farbe=cg.FARBE_KANTEN, striche=())
        yield "fertig", False

    def breitensuche(self):
        start = None
        if self.selected1 is None:
            try:
                start = next(iter(self.knoten))
            except:
                yield "Breitensuche fertig (es war nix da zum suchen)", False
        else:
            start = self.selected1

        zu_bearbeiten = [start]
        bekannt = {start}

        while zu_bearbeiten:
            aktuell = zu_bearbeiten.pop(0)
            self.knoten_design(aktuell, form=2, rand="green")
            yield f"Knoten {aktuell} ist in Bearbeitung"
            for nachbar in self.hole_nachbarknoten(aktuell):
                if nachbar in bekannt:
                    yield f"neuer Knoten {nachbar} schon bekannt"
                else:
                    self.knoten_design(nachbar, form=3, rand="yellow")
                    yield f"neuer Knoten {nachbar} gefunden"
                    bekannt.add(nachbar)
                    zu_bearbeiten.append(nachbar)
                    self.knoten_design(nachbar, form=1, rand="orange")
            self.knoten_design(aktuell, form=5, rand="red")
            yield f"Knoten {aktuell} ist fertig bearbeitet"
        yield "fertig", False

    def breitensuche_mit_ziel(self):
        ziel = self.selected2
        if ziel is None:
            yield "es muss ein Ziel angegeben werden", False

        start = None
        if self.selected1 is None:
            try:
                start = next(iter(self.knoten))
            except:
                yield "Breitensuche fertig (es war nix da zum suchen)", False
        else:
            start = self.selected1

        zu_bearbeiten = [start]
        bekannt = {start}

        while zu_bearbeiten:
            aktuell = zu_bearbeiten.pop(0)
            self.knoten_design(aktuell, form=2, rand="green")
            yield f"Knoten {aktuell} ist in Bearbeitung"
            for nachbar in self.hole_nachbarknoten(aktuell):
                if nachbar in bekannt:
                    yield f"neuer Knoten {nachbar} schon bekannt"
                else:
                    if nachbar is ziel:
                        yield f"Ziel {nachbar} gefunden", False
                    self.knoten_design(nachbar, form=3, rand="yellow")
                    yield f"neuer Knoten {nachbar} gefunden"
                    bekannt.add(nachbar)
                    zu_bearbeiten.append(nachbar)
                    self.knoten_design(nachbar, form=1, rand="orange")
            self.knoten_design(aktuell, form=5, rand="red")
            yield f"Knoten {aktuell} ist fertig bearbeitet"
        yield "fertig", False

    def kuerzester_weg_bfs(self):
        start = self.selected1
        if start is None:
            yield "es muss ein Start angegeben werden", False
        ziel = self.selected2
        if ziel is None:
            yield "es muss ein Ziel angegeben werden", False

        zu_bearbeiten = [start]
        bekannt = {start}

        while zu_bearbeiten:
            aktuell = zu_bearbeiten.pop(0)
            for nachbar in self.hole_nachbarknoten(aktuell):
                if nachbar not in bekannt:
                    if nachbar is ziel:
                        yield f"Ziel {nachbar} gefunden nach {...} Schritten", False
                    bekannt.add(nachbar)
                    zu_bearbeiten.append(nachbar)
        yield "Ziel nicht gefunden", False

    def markiere_knoten_iterativ(self):
        self.alle_knoten_aus()
        start = self.selected1
        if start is None: yield "Es muss ein Start-Knoten gewählt sein", False

        for kn in self.knoten:
            self.knoten_design(kn, form=2, rand="orange")
            yield f"Knoten {kn} markiert"
            self.knoten_design(kn, form=cg.FORM_KNOTEN, rand=cg.FARBE_KNOTEN_RAND)
        yield "fertig", False

    def kreisfreiheit(self):
        start = self.selected1
        if start is None or not isinstance(start, cg.Knoten):
            try:
                start = next(iter(self.knoten))  # irgendeinen Knoten wählen
            except StopIteration:
                yield "Der Graph enthält keine Knoten, ist also kreisfrei", False

        zu_bearbeiten = [start]
        bekannt = {start: None}  # dict statt set, der Erste hat keinen Vorgänger

        while zu_bearbeiten:
            aktuell = zu_bearbeiten.pop(0)
            self.knoten_design(aktuell, mitte="green", form=2)
            yield f"Knoten {aktuell} in Bearbeitung"

            for nachbar in self.hole_nachbarknoten(aktuell):
                self.knoten_design(nachbar, mitte="yellow", form=-4)
                yield f"Nachbar gefunden, prüfe, ob es der richtige Vorgänger ist"

                if nachbar in bekannt:
                    if nachbar is bekannt[aktuell]:
                        yield f"bekannter Nachbar gefunden, der ist Vorgänger, kein Kreis"
                        self.knoten_design(nachbar, mitte="orange", form=0)
                    else:
                        yield f"Kreis gefunden", False
                else:
                    self.knoten_design(nachbar, mitte="orange", form=0)
                    bekannt[nachbar] = aktuell
                    zu_bearbeiten.append(nachbar)

            self.knoten_design(aktuell, mitte="red", form=5)
            yield f"Knoten {aktuell} fertig bearbeitet"

    def ist_zusammenhaengend(self):
        start = self.selected1
        if start is None or not isinstance(start, cg.Knoten):
            try:
                start = next(iter(self.knoten))  # irgendeinen Knoten wählen
            except StopIteration:
                yield "Der Graph enthält keine Knoten, ist also kreisfrei", False

        zu_bearbeiten = [start]
        bekannt = {start}

        while zu_bearbeiten:
            aktuell = zu_bearbeiten.pop(0)

            for nb in self.hole_nachbarknoten(aktuell):
                if nb not in bekannt:
                    bekannt.add(nb)
                    zu_bearbeiten.append(nb)
        if len(bekannt) == len(self.knoten):
            yield "Der Graph ist zusammenhängend", False
        else:
            yield "Der Graph ist NICHT zusammenhängend", False

    def anzhal_zhk(self):
        anzahl = 0
        bekannt = set()
        for start in self.knoten:
            if start not in bekannt:
                anzahl += 1
                zu_bearbeiten = [start]

                while zu_bearbeiten:
                    aktuell = zu_bearbeiten.pop(0)
                    for nb in self.hole_nachbarknoten(aktuell):
                        if nb not in bekannt:
                            bekannt.add(nb)
                            zu_bearbeiten.append(nb)
        yield f"Der Graph hat {anzahl} ZHK", False

    def tiefensuche(self):
        def rek(aktuell:cg.Knoten):
            self.knoten_design(aktuell, form=3, rand="green")

            for nachbar in self.hole_nachbarknoten(aktuell):
                if nachbar not in bekannt:

                    self.knoten_design(nachbar, form=3, rand="yellow")
                    yield f"neuer Knoten {nachbar} gefunden"

                    bekannt.add(nachbar)

                    self.knoten_design(aktuell, form=3, rand="yellow")
                    yield f"neuer Knoten {nachbar} gefunden"

                    yield from rek(nachbar)
                    self.knoten_design(aktuell, form=3, rand="green")
            self.knoten_design(aktuell, form=2, rand="red")


        ziel = self.selected2
        if ziel is None:
            yield "es muss ein Ziel angegeben werden", False

        start = None
        if self.selected1 is None:
            try:
                start = next(iter(self.knoten))
            except:
                yield "Tiefensuche fertig (es war nix da zum suchen)", False
        else:
            start = self.selected1

        zu_bearbeiten = [start]
        bekannt = {start}
        self.knoten_design(start, form=3, rand="yellow")


        yield from rek(start)








graph = Graph(lade_graph='trabant.obj')
graph.starte_gui()
