import canvas_graph as cg

class Graph(cg.Graph):
    def __init__(self, **kwargs):
        cg.Graph.__init__(self, **kwargs)
        self.algo_hinzufuegen('Anzahl der Kanten an Konsole ausgeben', self.anzahl_kanten)
        self.algo_hinzufuegen("alle Kanten iterieren", self.makiere_kanten)
        self.algo_hinzufuegen("alle Knoten iterieren", self.makiere_knoten)
        self.algo_hinzufuegen('Breitensuche', self.breitensuche)
        self.algo_hinzufuegen('Breitensuche mit Ziel', self.breitensuche_mit_ziel)
        self.algo_hinzufuegen('Kreisfrei', self.kreisfrei)


    ################################### helper ###################################
    def hole_nachbarknoten(self, kn:cg.Knoten):
        for ka in self.kanten:
            if ka.von is kn:
                yield ka.nach
            elif ka.nach is kn:
                yield ka.von



    ################################### algos ###################################

    def kreisfrei(self):
        start = self.selected1
        if start is None or not isinstance(start, cg.Knoten):
            try:
                start = next(iter(self.knoten))
            except StopIteration:
                yield "Der Graph enthält keine Knoten, ist also kreisfrei", False

        zu_bearbeiten = [start]
        bekannt = {start: None}

        while zu_bearbeiten:
            aktuell = zu_bearbeiten.pop(0)
            self.knoten_design(aktuell, mitte='green', form=2)
            yield f'Knoten {aktuell} in Bearbeitung'

            for nachbar in self.hole_nachbarknoten(aktuell):
                self.knoten_design(nachbar, mitte='yellow', form=0)
                yield f'Nachbar gefunden, prüfe, ob es der richtige Vorgänger ist'
                if nachbar in bekannt:
                    if nachbar is bekannt[aktuell]:
                        yield f'bekannter Nachbar gefunden, der ist Vorgänger, kein Kreis'
                        self.knoten_design(aktuell, mitte='orange', form=0)
                    else:
                        yield f'Kreis gefunden', False
                        ... # noch kein kreis
                else:
                    bekannt[nachbar]=aktuell
                    zu_bearbeiten.append(nachbar)

            self.knoten_design(aktuell, mitte='red', form=1)
            yield f'Knoten {aktuell} fertig bearbeitet'

    def anzahl_kanten(self):
        yield f'Der Graph hat {len(self.kanten)} Kanten.', False


    def makiere_kanten(self):
        for ka in self.kanten:
            self.kanten_design(ka, farbe='blue', striche=(2,1))
            yield f'Kante {ka} makiert'
            self.kanten_design(ka, farbe=cg.FARBE_KANTEN, striche=())
        yield 'fertig', False

    def makiere_knoten(self):
        for kn in self.knoten:
            self.knoten_design(kn, form=2, rand='red')
            yield f'Knoten {kn} makiert'
            self.knoten_design(kn, form=cg.FORM_KNOTEN, rand=cg.FARBE_KNOTEN_RAND)
        yield 'fertig', False

    def breitensuche(self):
        if self.selected1 is None:
            yield 'Startknoten muss geählt sein', False
            try:
                start = next(iter(self.knoten))
            except:
                yield 'Breitensuche fertig (es wurde nichts zum Suchen gefunden)', False
        else:
            start = self.selected1

        zu_bearbeiten = [start]
        bekannt = {start}

        while zu_bearbeiten:
            aktuell = zu_bearbeiten.pop(0)
            self.knoten_design(aktuell, form=2, rand='green')
            yield f'Knoten {aktuell} ist in Bearbeitung'
            for nachbar in self.hole_nachbarknoten(aktuell):
                if nachbar in bekannt:
                    yield f'Nachbar {nachbar} schon bekannt'
                else:
                    self.knoten_design(nachbar, form=3, rand="yellow")
                    yield f'neuer Knoten {nachbar} makiert'
                    bekannt.add(nachbar)
                    zu_bearbeiten.append(nachbar)
                    self.knoten_design(nachbar, form=5, rand="orange")
            self.knoten_design(aktuell, form=5, rand="red")
            yield f'Knoten {aktuell} ist fertig bearbeitet'

        yield 'fertig', False

    def breitensuche_mit_ziel(self):
        if self.selected1 is None:
            yield 'Startknoten muss geählt sein', False
            try:
                start = next(iter(self.knoten))
            except:
                yield 'Breitensuche fertig (es wurde nichts zum Suchen gefunden)', False
        else:
            start = self.selected1

        if self.selected2 is None:
            yield 'Zielknoten muss gewählt sein', False

        else:
            ziel = self.selected2


        zu_bearbeiten = [start]
        bekannt = {start}

        while zu_bearbeiten:
            aktuell = zu_bearbeiten.pop(0)
            self.knoten_design(aktuell, form=2, rand='green')
            yield f'Knoten {aktuell} ist in Bearbeitung'
            for nachbar in self.hole_nachbarknoten(aktuell):
                if nachbar in bekannt:
                    yield f'Nachbar {nachbar} schon bekannt'
                else:
                    if nachbar is ziel:
                        yield f'Ziel {nachbar} gefunden', False
                    self.knoten_design(nachbar, form=3, rand="yellow")
                    yield f'neuer Knoten {nachbar} makiert'
                    bekannt.add(nachbar)
                    zu_bearbeiten.append(nachbar)
                    self.knoten_design(nachbar, form=5, rand="orange")
            self.knoten_design(aktuell, form=5, rand="red")
            yield f'Knoten {aktuell} ist fertig bearbeitet'

        yield 'fertig', False


    def kuerzester_weg_bfs(self):
        if self.selected1 is None:
            yield 'Startknoten muss geählt sein', False
            try:
                start = next(iter(self.knoten))
            except:
                yield 'Breitensuche fertig (es wurde nichts zum Suchen gefunden)', False
        else:
            start = self.selected1

        if self.selected2 is None:
            yield 'Zielknoten muss gewählt sein', False
        else:
            ziel = self.selected2


        zu_bearbeiten = [start]
        bekannt = {start}

        while zu_bearbeiten:
            aktuell = zu_bearbeiten.pop(0)
            for nachbar in self.hole_nachbarknoten(aktuell):
                if nachbar not in bekannt:
                    if nachbar is ziel:
                        yield f'Ziel {nachbar} gefunden', False
                    bekannt.add(nachbar)
                    zu_bearbeiten.append(nachbar)
            yield f'Knoten {aktuell} ist fertig bearbeitet'

        yield 'fertig', False




graph = Graph()
graph.lade_graph("graphen/Komponenten.graph")
graph.starte_gui()