class Knoten:
    def __init__(self, name: str, kommentar: str | None = None):
        self.__name = name
        self.__kommentar = kommentar

    def __eq__(self, other):
        if other is None: return False
        if not isinstance(other, Knoten): return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name

    @property
    def kommentar(self):
        return self.__kommentar

    @property
    def name(self):
        return self.__name


class Kante:
    def __init__(self, von: Knoten, nach: Knoten,
                 gerichtet: bool = True,
                 gewicht: float | None = None,
                 version: int | None = None,
                 kommentar: str | None = None):
        self.__von: Knoten = von
        self.__nach: Knoten = nach
        self.__gewicht: float | None = gewicht
        self.__gerichtet: bool = gerichtet
        self.__kommentar = kommentar
        self.__version = version

    def __eq__(self, other):
        if other is None: return False # kein Objekt
        if not isinstance(other, Kante): return False# falscher Typ
        t_self = (self.von, self.nach, self.__version) # self
        t_other1 = (other.von, other.nach, other.__version) # other in der gleichen Richtung
        if t_self == t_other1: return True  # so sind gerichtete und ungerichtete Kanten gleich
        t_other2 = (other.nach, other.von, other.__version) # # other in der anderen Richtung
        if not self.ist_gerichtet and t_self == t_other2: return True  # so sind ungerichtete Kanten AUCH gleich
        return False # dann sind sie ungleich

    def __hash__(self):
        if self.ist_gerichtet:
            return hash((self.von, self.nach, self.__version))
        else: # ungerichtet → von/nach und nach/von muss gleich sein
            return hash(self.von) ^ hash(self.nach) ^ hash(self.__version)  # xor, dann ist die Reihenfolge wurscht

    def __repr__(self):
        return (f"{self.von}"
                f"{f'->' if self.ist_gerichtet else '-'}"
                f"{self.nach}"
                f"{'' if self.__version is None else f'_v{self.__version}'}"
                f"{'' if self.gewicht is None else f' ({self.gewicht})'}")

    @property
    def ist_gerichtet(self):
        return self.__gerichtet

    @property
    def gewicht(self):
        return self.__gewicht

    @property
    def kommentar(self):
        return self.__kommentar

    @property
    def nach(self):
        return self.__nach

    @property
    def von(self):
        return self.__von


class Graph:
    def __init__(self,
                 lade_graph: str = None,
                 multi_graph: bool = False,
                 gerichtet: bool = False,
                 gewichtet: bool = False
                 ):
        """
        Graph-Repräsentation
        :param lade_graph: Lädt direkt diese Graph-Datei, wenn angegeben.
        :param multi_graph: Legt fest, ob es Mehrfachkanten geben darf.
        :param gerichtet: Legt fest, ob Kanten geRichtet sind.
        :param gewichtet: Legt fest, ob Kanten geWichtet sind.
        """
        self._multi_graph: bool = multi_graph  # ob Mehrfachkanten möglich sind
        self._gerichtet: bool = gerichtet  # ob die Kanten geRichtet sind
        self._gewichtet: bool = gewichtet  # obv die Kanten geWichtet sind

        self.__knoten_dict: dict[str, Knoten] = {}
        self.__kanten_dict: dict[str, Kante] = {}

        self._datei_zeilen = []  # Leerzeilen, Kommentare, Knoten und Kanten der gelesenen bzw zu schreibenden Datei
        if lade_graph is not None:
            self.lade_graph(lade_graph)

    def __str__(self):
        return (f"Knoten: {'; '.join(map(str,self.knoten))}\n"
                f"Kanten: {', '.join(map(str, self.kanten))}")

    @property
    def ist_gerichtet(self):
        return self._gerichtet

    @property
    def ist_gewichtet(self):
        return self._gewichtet

    @property
    def ist_multi_graph(self):
        return self._multi_graph

    @property
    def kanten(self):
        return iter(self.__kanten_dict.values())

    @property
    def knoten(self):
        return iter(self.__knoten_dict.values())


    def lade_graph(self, dateiname: str) -> None:
        with (open(dateiname, "rt") as d):

            self._datei_zeilen = []
            self.__knoten_dict.clear()
            self.__kanten_dict.clear()

            for zeile in d:
                if zeile.strip() == "":  # Leerzeile
                    self._datei_zeilen.append('')
                elif zeile.strip().startswith('#'):  # Kommentarzeile
                    self._datei_zeilen.append(zeile)
                else:  # Knoten oder Kante oder Müll
                    inhalt_kommentar = zeile.split('#', maxsplit=1)  # Kommentar suchen
                    if len(inhalt_kommentar) == 1:
                        inhalt = inhalt_kommentar[0]
                        kommentar = None
                    else:
                        inhalt, kommentar = inhalt_kommentar
                    if ";" in inhalt:  # Knoten
                        name, _, _ = inhalt.strip().split(";")
                        kn = Knoten(name, kommentar=kommentar)
                        self.__knoten_dict[name] = kn
                        self._datei_zeilen.append(kn)
                    elif "," in inhalt:  # Kante
                        von_nach_gewicht = inhalt.strip().split(",", maxsplit=2)
                        if len(von_nach_gewicht) == 2:  # von, nach
                            von, nach = von_nach_gewicht
                            gewicht = 1 if self.ist_gewichtet else None
                        else:  # von, nach, gewicht
                            von, nach, gewicht = von_nach_gewicht

                        if self.ist_multi_graph:
                            version = 1
                            while f"{von}#{nach}#{version}" in self.__kanten_dict:
                                version += 1
                            ka = Kante(self.__knoten_dict[von], self.__knoten_dict[nach],
                                       gewicht=gewicht,
                                       gerichtet=self.ist_gerichtet,
                                       version=version,
                                       kommentar=kommentar)
                            self.__kanten_dict[f"{von}#{nach}#{version}"] = ka
                            self._datei_zeilen.append(ka)
                        else:
                            if f"{von}#{nach}" in self.__kanten_dict:
                                print(f"Kante aus Datei {dateiname} ignoriert ({zeile.strip()}) - kein Multigraph")
                            else:
                                ka = Kante(self.__knoten_dict[von], self.__knoten_dict[nach],
                                           gewicht=gewicht,
                                           gerichtet=self.ist_gerichtet,
                                           kommentar=kommentar)
                                self.__kanten_dict[f"{von}#{nach}"] = ka
                                self._datei_zeilen.append(ka)

if __name__ == "__main__":
    app = Graph(lade_graph="graphen/Drachen.graph")
    print(app)


    print()
    print(*app.knoten)
    print(*app.kanten)
