import basis_graph
import tkinter as tk
import tkinter.filedialog as fd
from tkinter.ttk import Combobox
# from PIL import Image, ImageTk # wenn PIL installiert ist, können Bilder skaliert werden
import os, platform
from typing import Iterator, Callable, Literal

# Optik
LINIEN_DICKE = 6
KNOTEN_RADIUS = 15
PFEIL_FORM = (12, 25, 15)  # Länge der Spitze am Schaft, Länge Außenseite der Spitze, Länge Schaft/Außenecke
FARBE_AUSWAHL = "lightgreen"  # Farbe ausgewählter Objekte erstes/Start/Anfang mit links click
FARBE_AUSWAHL_2 = "red"  # Farbe ausgewählter Objekte zweites/Ziel/Ende mit rechts click
FARBE_KANTEN_GEWICHTE = "black"
FARBE_KNOTEN_MITTE = "grey60"
FARBE_KNOTEN_RAND = "black"
FARBE_KANTEN = "grey20"
FARBE_TEMP_KANTEN = "black"  # die Kanten, während man sie hinzufügt

# Verhalten
ALGO_PAUSE_ZEIT = 1200  # Wartezeit in ms bei automatischer Ausführung von Algos
KLICK_DIST = 5  # wie weit man höchstens von Objekten entfernt klicken muss, um sie zu treffen
ZOOM_FAKTOR_REIN = 1.1
ZOOM_FAKTOR_RAUS = 1 / ZOOM_FAKTOR_REIN

# Technik
OS = platform.system()  # "Linux", "Windows", "Darwin" (MacOS), andere?


##################################################### Knoten ######################################################

class Knoten(basis_graph.Knoten):
    def __init__(self, canvas: tk.Canvas,
                 name: str, x: float, y: float, r: float = KNOTEN_RADIUS,
                 kommentar: str | None = None):
        basis_graph.Knoten.__init__(self, name, kommentar=kommentar)

        self._canvas: tk.Canvas = canvas
        self.x: float = x
        self.y: float = y
        self.r: float = r

        self.canvas_id = self._canvas.create_oval(-self.r, -self.r, self.r, self.r,
                                                  width=LINIEN_DICKE,
                                                  fill=FARBE_KNOTEN_MITTE,
                                                  outline=FARBE_KNOTEN_RAND)
        self._canvas.tag_raise(self.canvas_id)

        # font-Größe dynamisch anpassen, damit die Beschriftung in den Kreis passt
        font_size = int(2 * self.r)  # der Durchmesser des Kreises ist eine gute Obergrenze
        self.text_id = self._canvas.create_text(0, 0, text=self.name, font=('courier', font_size, "bold"))
        self._canvas.tag_raise(self.text_id)
        while True:
            self._bbx1, self._bby1, self._bbx2, self._bby2 = self._canvas.bbox(self.text_id)
            if ((self._bbx2 - self._bbx1) < 2 * self.r - LINIEN_DICKE // 2 and
                    (self._bby2 - self._bby1) < 2 * self.r - LINIEN_DICKE // 2): break
            font_size -= 1
            self._canvas.itemconfigure(self.text_id, font=('courier', font_size, "bold"))
        self._text_off_x = self._text_off_y = LINIEN_DICKE // 2 - 2

    def update(self, delta_x: float = 0, delta_y: float = 0):
        self.x += delta_x
        self.y += delta_y
        self._canvas.coords(self.canvas_id, self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r)
        self._canvas.coords(self.text_id, self.x + self._text_off_x, self.y + self._text_off_y)


########################################## Ende von Knoten #############################################

################################################ Kante #############################################
class Kante(basis_graph.Kante):
    def __init__(self, canvas: tk.Canvas, name: str, von: Knoten, nach: Knoten,
                 multi_kante: "CanvasMultiKante",
                 gerichtet: bool = True,
                 gewicht: float | None = None,
                 version: int | None = None,
                 kommentar: str | None = None):
        basis_graph.Kante.__init__(self, von, nach, gerichtet=gerichtet, gewicht=gewicht,
                                   version=version, kommentar=kommentar)
        self._canvas: tk.Canvas = canvas
        self.multi_kante = multi_kante
        self.name: str = name

        line_args = {'arrow': "last", 'arrowshape': PFEIL_FORM} if self.ist_gerichtet else {}
        self.canvas_id = self._canvas.create_line(self.von.x, self.von.y, self.nach.x, self.nach.y,
                                                  width=LINIEN_DICKE, fill=FARBE_KANTEN, **line_args)
        if self.gewicht is None:
            self.text_id = None
        else:
            self.text_id = self._canvas.create_text(0, 0,
                                                    text=str(self.gewicht),
                                                    font=('courier', PFEIL_FORM[2] * 2, "bold"),
                                                    fill=FARBE_KANTEN_GEWICHTE)

    @property
    def nach(self) -> Knoten:
        return self.__nach

    @property
    def von(self) -> Knoten:
        return self.__von


############################################# Ende von Kante #############################################

############################################# CanvasMultiKante ##########################################

class CanvasMultiKante:
    """
    Eine CanvasMultiKante bildet alle Kanten zwischen zwei Knoten ab.
    Es ist egal, ob die Kanten gerichtet sind oder nicht oder ob Mehrfachkanten dabei sind.
    Es gibt zwischen zwei Knoten höchstens eine solche Kante auf dem Canvas (Richtung und Anzahl egal).
    """

    def __init__(self, canvas: tk.Canvas, name: str, von: Knoten, nach: Knoten):
        self._canvas: tk.Canvas = canvas
        self.name = name
        self.von: Knoten = von
        self.nach: Knoten = nach

        self.kanten_dict: dict[str, Kante] = {}  # {name: Kante}

    def neue_kante(self, name: str,
                   von: Knoten, nach: Knoten,
                   gerichtet: bool = True,
                   gewicht: float | None = None,
                   version: int | None = None,
                   kommentar: str | None = None) -> Kante:
        k = Kante(self._canvas, name, von, nach, multi_kante=self,
                  gerichtet=gerichtet, gewicht=gewicht, version=version, kommentar=kommentar)
        self.kanten_dict[k.name] = k
        return k

    def entferne_kante(self, name: str):
        del self.kanten_dict[name]

    def update(self):
        l = len(self.kanten_dict)
        lm1h = (l - 1) / 2
        b = PFEIL_FORM[2] * 2
        offsets = [b * (i - lm1h) for i in range(l)]  # bei mehreren Kanten müssen diese seitlich verschoben werden

        for offset, k in enumerate(self.kanten_dict.values()):
            # die Linien bis zum Rand der Knoten verkürzen
            # man könnte die Linien auch nur hinter die Knoten malen, aber dann gibts keine Pfeile
            xd = k.nach.x - k.von.x
            yd = k.nach.y - k.von.y

            d = (xd ** 2 + yd ** 2) ** .5
            if d > 0:
                f = KNOTEN_RADIUS / d
                off_x = -offsets[offset] * (yd / d)
                off_y = offsets[offset] * (xd / d)

                if self.von != k.von:
                    off_x = -off_x
                    off_y = -off_y

                fx, fy = f * xd, f * yd
                self._canvas.coords(k.canvas_id,
                                    k.von.x + fx + off_x, k.von.y + fy + off_y,
                                    k.nach.x - fx + off_x, k.nach.y - fy + off_y)
                if k.gewicht is not None:
                    # diesen Text könnte man auch noch entlang der Kanten verteilen, statt alle jeweils in die Mitte zu machen
                    self._canvas.coords(k.text_id,
                                        (k.von.x + k.nach.x) / 2 + off_x,
                                        (k.von.y + k.nach.y) / 2 + off_y)


####################################### Ende von CanvasMultiKante #########################################

################################################### Graph #################################################


class Graph(
    basis_graph.Graph):  # absichtlich nicht (auch) von Tk erben, damit das Interface dieser Klasse so klein wie möglich bleibt
    """
        Graph mit GUI
        - links klicken auf Knoten oder Kante → markieren / un-markieren Erster/Anfang/Start
        - links klicken auf Canvas → un-markieren Erster/Anfang/Start
        - rechts klicken auf Knoten oder Kante → markieren/un-markieren Letzter/Ende/Ziel
        - rechts klicken auf Canvas → neuer Knoten
        - Knoten mit links ziehen → Knoten bewegen
        - Knoten mit rechts ziehen → Neue Kante einbauen ab diesem Knoten, muss auf anderem Knoten losgelassen werden
        - Scollen → Zoomen
        - ENFERNEN bei markierter Kante (Erster/Anfang/Start) → markierte Kante wird entfernt
        - ENFERNEN bei markiertem Knoten (Erster/Anfang/Start) → markierter Knoten wird entfernt, wenn er keine Kanten hat
        - PFEIL-HOCH/RUNTER/LINKS/RECHTS bei markiertem Knoten → Knoten ein Pixel hoch/runter/links/rechts
        - Algo in erbender Klasse als Methode schreiben und registrieren → Algo in Drop-Down
        - im Drop-Down Algo wählen → Start möglich
        - Start → führt Algo aus (je nach auto, automatisch oder manuell)
        - Stop → bricht Algo ab
        - Weiter → nächster Schritt, wenn Algo manuell ausgeführt wird
        - auto an → nächster Schritt automatisch
        - auto aus → nächster Schritt manuell
    """

    def __init__(self,
                 lade_graph: str = None,
                 multi_graph: bool = False,
                 gerichtet: bool = False,
                 gewichtet: bool = False):
        basis_graph.Graph.__init__(self,
                                   multi_graph=multi_graph,
                                   gerichtet=gerichtet,
                                   gewichtet=gewichtet)

        self._knoten_dict: dict[str, Knoten] = {}
        self._kanten_dict: dict[str, Kante] = {}
        self._multi_kanten_dict: dict[str, CanvasMultiKante] = {}
        self._canvas_id_dict: dict[int, Knoten | Kante] = {}

        self._drag_links_id: int | None = None  # ID des geklickten Dings
        self._drag_links_nur_click: bool = True  # ob ein geklickter Knoten, noch nicht bewegt wurde
        self._drag_links_start_x: float | None = None
        self._drag_links_start_y: float | None = None

        self._drag_rechts_nur_click: bool = True  # ob ein geklickter Knoten, noch nicht bewegt wurde
        self._drag_rechts_start_x: float | None = None
        self._drag_rechts_start_y: float | None = None
        self._drag_rechts_start_knoten_id: int | None = None  # Startknoten für neue Kante
        self._drag_rechts_temp_line: int | None = None  # temporäre Grafik der neu anzulegenden Kante

        self._fenster = tk.Tk()
        self._fenster.geometry("1220x720")

        self.canvas = tk.Canvas(master=self._fenster)
        self.canvas.pack(side="bottom", expand=True, fill="both")
        # self._hintergrundbild_original: Image.Image | None = None           # mit PIL statt der nächsten
        self._hintergrundbild_original: tk.PhotoImage | None = None
        # self._hintergrundbild_resized: ImageTk.PhotoImage | None = None     # mit PIL
        self._canvas_background_id: int | None = None  # canvas id | None

        frm_text = tk.Frame(master=self._fenster)
        frm_text.pack(side="bottom", anchor="w", fill="x")
        frm_btns_algo = tk.Frame(master=self._fenster, relief="solid", bd=1)
        frm_btns_algo.pack(side="left", padx=5, pady=5)
        frm_btns_graph = tk.Frame(master=self._fenster, relief="solid", bd=1)
        frm_btns_graph.pack(side="left", padx=5, pady=5)
        frm_lbls = tk.Frame(master=self._fenster, relief="solid", bd=1)
        frm_lbls.pack(side="left", padx=5, pady=5)

        self._combo_algos = Combobox(master=frm_text, state="readonly", values=[""], width=30, font=("Arial", 16))
        self._combo_algos.pack(side="left", anchor="w", padx=5)
        self._lbl_out = tk.Label(master=frm_text, text="", font=("Arial", 12))
        self._lbl_out.pack(side="left", anchor="center", fill="x", padx=20)

        # graph + Fenster Buttons
        self.selected: Knoten | Kante | None = None  # das auf dem Canvas gewählte Ding (Kante oder Knoten)
        self.selected2: Knoten | Kante | None = None  # das auf dem Canvas gewählte Ding (Kante oder Knoten)
        self._btn_laden = tk.Button(master=frm_btns_graph, text="laden", command=self.lade_graph_datei)
        self._btn_laden.pack(side="left", padx=5, pady=5)
        self._btn_speichern = tk.Button(master=frm_btns_graph, text="speichern", command=self._graph_speichern)
        self._btn_speichern.pack(side="left", padx=5, pady=5)
        self._btn_ausgeben = tk.Button(master=frm_btns_graph, text="ausgeben", command=lambda: print(self))
        self._btn_ausgeben.pack(side="left", padx=5, pady=5)
        tk.Button(master=frm_btns_graph, text="beenden", command=self._fenster.destroy).pack(side="left", padx=5,
                                                                                             pady=5)

        # algo-Logik
        self._algo_dict: dict[str, Callable] = {}  # dictionary der Algos
        self.running = False  # ob ein laufender Algo abgebrochen werden soll
        self._algo: Callable | None = None  # der aktuell eingestellte Algo
        self._algo_iter: Iterator[str] | None = None  # der Iterator des laufenden Algos
        self._algo_letzte: str = ""  # letzte Nachricht des laufenden Algos

        self._btn_startstop_toggle = tk.Button(master=frm_btns_algo, text="start", width="5", state="disabled",
                                               command=self._startstop_toggle)  # Start / Stop (eines Algos)
        self._btn_startstop_toggle.pack(side="left", padx=5, pady=5)
        self._btn_algo_weiter = tk.Button(master=frm_btns_algo, text="weiter",
                                          command=self._algo_weiter, state="disabled")  # (Algo manuell) weiter
        self._btn_algo_weiter.pack(side="left", padx=5, pady=5)
        self._var_cb_auto = tk.IntVar(value=1)  # Variable für CheckBox auto
        self._cb_auto = tk.Checkbutton(master=frm_btns_algo, text="auto", variable=self._var_cb_auto,
                                       state="disabled", command=self._cb_auto_toggle)  # CheckBox auto
        self._cb_auto.pack(side="left", padx=5, pady=5)
        self._btn_reset = tk.Button(master=frm_btns_algo, text="Farb-Reset", command=self.reset)
        self._btn_reset.pack(side="left", padx=5, pady=5)

        # Labels
        tk.Label(master=frm_lbls, text="Multigraph\n" + ("ja" if self._multi_graph else "nein")
                 ).pack(side="left", padx=5, pady=0)
        tk.Label(master=frm_lbls, text="Kantengewichte\n" + ("ja" if self.ist_gewichtet else "nein")
                 ).pack(side="left", padx=5, pady=0)
        tk.Label(master=frm_lbls, text="gerichtet\n" + ("ja" if self.ist_gerichtet else "nein")
                 ).pack(side="left", padx=5, pady=0)
        self._lbl_knoten_zahl = tk.Label(master=frm_lbls, text="Knoten\n0")
        self._lbl_knoten_zahl.pack(side="left", padx=5, pady=0)
        self._lbl_kanten_zahl = tk.Label(master=frm_lbls, text="Kanten\n0")
        self._lbl_kanten_zahl.pack(side="left", padx=5, pady=0)

        # Events
        self._maus_unten: Literal["links", "rechts"] | None = None
        if OS == "Linux":  # (+ andere?)
            self.canvas.bind('<4>', self._zoom)
            self.canvas.bind('<5>', self._zoom)
        else:  # Windows + MacOS (+ andere?)
            self.canvas.bind("<MouseWheel>", self._zoom)

        self.canvas.bind('<ButtonPress-1>', self._drag_links_start)
        self.canvas.bind('<B1-Motion>', self._drag_links_weiter)
        self.canvas.bind('<ButtonRelease-1>', self._drag_links_stop)

        self.canvas.bind('<ButtonPress-3>', self._drag_rechts_start)
        self.canvas.bind('<B3-Motion>', self._drag_rechts_weiter)
        self.canvas.bind('<ButtonRelease-3>', self._drag_rechts_stop)

        self._fenster.bind('<Delete>', self._delete)
        self._fenster.bind('<Up>', self._pfeiltaste_hoch)
        self._fenster.bind('<Left>', self._pfeiltaste_links)
        self._fenster.bind('<Right>', self._pfeiltaste_rechts)
        self._fenster.bind('<Down>', self._pfeiltaste_runter)

        self.canvas.bind('<Configure>', self._canvas_resize)

        self._combo_algos.bind('<<ComboboxSelected>>', self._combo_select)

        # los gehts
        if lade_graph is not None:
            self.lade_graph(lade_graph)

    def __str__(self):
        return (f"{basis_graph.Graph.__str__(self)}\n"
                f"Auswahl 1: {'nix' if self.selected is None else self.selected}, "
                f"Auswahl 2: {'nix' if self.selected2 is None else self.selected2}")

    @property  # basis_graph property überschreiben, damit die Typen der Kanten von hier sind
    def kanten(self):
        return iter(self._kanten_dict.values())

    @property  # basis_graph property überschreiben, damit die Typen der Knoten von hier sind
    def knoten(self):
        return iter(self._knoten_dict.values())

    ################### Methoden (außer Properties, Callbacks und Algo-Logik) ##################################

    def algo_hinzufuegen(self, name: str, funktion: Callable):
        self._algo_dict[name] = funktion
        self._combo_algos['values'] = (*self._combo_algos['values'], name)

    def _graph_speichern(self):
        if self.running: return  # nicht, wenn gerade ein Algo läuft
        dateiname = fd.asksaveasfilename(initialdir=os.path.realpath(__file__),
                                         filetypes=(("Graph Datei", "*.grf *.graph"),))
        if dateiname:
            with open(dateiname, "wt") as datei:
                elem: str | Knoten | Kante
                for elem in self._datei_zeilen:
                    if (t := type(elem)) == str:
                        datei.write(f"{elem}")
                    elif t == Knoten:
                        datei.write(f"{elem.name};{int(elem.x)};{int(elem.y)}"
                                    f"{"\n" if elem.kommentar is None else f' #{elem.kommentar}'}")
                    elif t == Kante:
                        datei.write(f"{elem.von.name},{elem.nach.name}"
                                    f"{f',{int(elem.gewicht)}' if self.ist_gewichtet else ''}"
                                    f"{"\n" if elem.kommentar is None else f' #{elem.kommentar}'}")

    def _hole_canvas_id_bei_maus(self, x: float, y: float, typen: tuple | None = None) -> int | None:
        canvas_ids = self.canvas.find_overlapping(x - KLICK_DIST, y - KLICK_DIST, x + KLICK_DIST, y + KLICK_DIST)
        for canvas_id in canvas_ids:
            if canvas_id in self._canvas_id_dict:
                if typen is None or type(self._canvas_id_dict[canvas_id]) in typen:
                    return canvas_id
        return None

    def lade_graph(self, dateiname: str) -> None:
        if self.running: return  # nicht, wenn gerade ein Algo läuft
        if not os.path.exists(dateiname):
            print(f"Datei <{dateiname}> nicht gefunden")
            return

        try:
            with open(dateiname, "rt") as d:
                self._datei_zeilen.clear()
                self._knoten_dict.clear()
                self._kanten_dict.clear()
                self._multi_kanten_dict.clear()
                self._canvas_id_dict.clear()

                self.canvas.delete("all")
                self._lade_hintergrund()

                for zeile in d:
                    if zeile.strip() == "":  # Leerzeile
                        self._datei_zeilen.append(zeile)
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
                            name, x, y = inhalt.strip().split(";")
                            self._neuer_knoten(name, int(x), int(y), kommentar=kommentar, insert=False)

                        elif "," in inhalt:  # Kante
                            von_nach_gewicht = inhalt.strip().split(",", maxsplit=2)
                            if len(von_nach_gewicht) == 2:  # von, nach
                                von, nach = von_nach_gewicht
                                gewicht = 1 if self.ist_gewichtet else None
                            else:  # von, nach, gewicht
                                von, nach, gewicht = von_nach_gewicht
                            self._neue_kante(von, nach, gewicht, kommentar)

            self._update()
        except OSError as e:
            print(e, e.args)

    def lade_graph_datei(self):
        if self.running: return  # nicht, wenn gerade ein Algo läuft
        dateiname = fd.askopenfilename(initialdir=os.path.realpath(__file__),
                                       filetypes=(("Graph Datei", "*.grf *.graph"),))
        if isinstance(dateiname, str) and dateiname:  # bei Abbruch ist es ein leeres Tupel
            print(dateiname)
            self.lade_graph(dateiname)

    def _lade_hintergrund(self):
        if self._hintergrundbild_original is not None:
            # x = self.canvas.winfo_width() # mit PIL
            # y = self.canvas.winfo_height() # mit PIL
            # resized = self._hintergrundbild_original.resize((x, y)) # mit PIL
            # self._hintergrundbild_resized = ImageTk.PhotoImage(resized) # mit PIL
            if self._canvas_background_id is None or self._canvas_background_id not in self.canvas.find_all():
                # mit PIL statt der nächsten
                # self._canvas_background = self.canvas.create_image(0, 0, image=self._hintergrundbild_resized, anchor="nw")
                self._canvas_background_id = self.canvas.create_image(0, 0, image=self._hintergrundbild_original,
                                                                      anchor="nw")
                self.canvas.tag_lower(self._canvas_background_id)
            else:
                # mit PIL statt der nächsten
                # self.canvas.itemconfigure(self._canvas_background, image=self._hintergrundbild_resized)
                self.canvas.itemconfigure(self._canvas_background_id, image=self._hintergrundbild_original)

    def lade_hintergrund_datei(self, bilddatei: str):
        try:
            # mit PIL statt der nächsten
            # self._hintergrundbild_original = Image.open(bilddatei)
            self._hintergrundbild_original = tk.PhotoImage(file=bilddatei)
        except Exception as e:
            print(e, e.args)

    def _neuer_knoten(self, name: str, x: int, y: int, kommentar: str | None = None, insert: bool = True):
        if self.running: return  # nicht, wenn gerade ein Algo läuft
        kn = Knoten(self.canvas, name, int(x), int(y), kommentar=kommentar)
        self._knoten_dict[name] = kn
        self._canvas_id_dict[kn.canvas_id] = kn

        if insert:
            i = 0
            letzter_knoten = None
            while i < len(self._datei_zeilen):
                if type(self._datei_zeilen[i]) == Knoten: letzter_knoten = i
                i += 1
            if letzter_knoten is None:
                self._datei_zeilen.append(kn)
            else:
                self._datei_zeilen.insert(letzter_knoten + 1, kn)
        else:
            self._datei_zeilen.append(kn)

        self._update(canvas_obj=kn)

    def _neue_kante(self, von: str, nach: str, gewicht: int | None = None, kommentar: str | None = None):
        if self.running: return  # nicht, wenn gerade ein Algo läuft
        k_von = self._knoten_dict[von]
        k_nach = self._knoten_dict[nach]

        # internen namen der Kante ermitteln
        base_name = f"{von}#{nach}"
        base_name_r = f"{nach}#{von}"

        if self.ist_multi_graph:
            version = 1
            while f"{base_name}#{version}" in self._kanten_dict:
                version += 1
            name = f"{base_name}#{version}"
        else:
            version = None
            if base_name in self._kanten_dict or (not self.ist_gerichtet and base_name_r in self._kanten_dict):
                print(f"Kante von {von} nach {nach} ignoriert (kein Multigraph)")
                return
            else:
                name = base_name

        # passende CanvasMultiKante suchen oder erstellen
        if base_name in self._multi_kanten_dict:
            mk = self._multi_kanten_dict[base_name]
        elif base_name_r in self._multi_kanten_dict:
            mk = self._multi_kanten_dict[base_name_r]
        else:
            mk = CanvasMultiKante(self.canvas, base_name, k_von, k_nach)
        self._multi_kanten_dict[base_name] = mk
        # CanvasKante erstellen und überall einfügen
        ka = mk.neue_kante(name=name,
                           von=k_von, nach=k_nach,
                           gerichtet=self._gerichtet,
                           gewicht=gewicht,
                           version=version,
                           kommentar=kommentar)
        self._kanten_dict[name] = ka
        self._canvas_id_dict[ka.canvas_id] = ka
        self._datei_zeilen.append(ka)
        self._update(canvas_obj=ka)

    def starte_gui(self):
        self._fenster.mainloop()

    ###################################### GUI Callbacks ###########################################################

    def _canvas_resize(self, event: tk.Event):
        self._lade_hintergrund()

    def _combo_select(self, event: tk.Event):
        self._algo_stop()
        if self._combo_algos.get():
            self._algo = self._algo_dict[self._combo_algos.get()]
            self._btn_startstop_toggle.config(state="active")
            self._cb_auto.config(state="active")
        else:
            self._btn_startstop_toggle.config(state="disabled")
            self._cb_auto.config(state="disabled")

    def _delete(self, event: tk.Event):
        if self.running: return
        if self._maus_unten is not None: return
        if self.selected is None: return
        if isinstance(self.selected, Kante):
            self._multi_kanten_dict[self.selected.multi_kante.name].entferne_kante(self.selected.name)
            del self._kanten_dict[self.selected.name]
        elif isinstance(self.selected, Knoten):
            for ka in self.kanten:  # Knoten mit Kanten kann man nicht löschen
                if ka.von is self.selected or ka.nach is self.selected:
                    print(f"Knoten {self.selected} hat noch Kanten (z.B. {ka}) => wird nicht gelöscht")
                    return
            del self._knoten_dict[self.selected.name]
        else:
            return
        if self.selected.text_id is not None: self.canvas.delete(self.selected.text_id)
        self._datei_zeilen.remove(self.selected)
        del self._canvas_id_dict[self.selected.canvas_id]
        self.canvas.delete(self.selected.canvas_id)
        self.selected = None

    def _drag_links_start(self, event: tk.Event):
        self._maus_unten = "links"
        self._drag_links_start_x = event.x
        self._drag_links_start_y = event.y
        self._drag_links_id = self._hole_canvas_id_bei_maus(event.x, event.y, (Knoten, Kante))
        self._drag_links_nur_click = True

    def _drag_links_weiter(self, event: tk.Event):
        self._drag_links_nur_click = False
        if self._drag_links_id is not None and isinstance(self._canvas_id_dict[self._drag_links_id], Knoten):
            # Knoten => bewegen
            self._update(delta_x=event.x - self._drag_links_start_x,
                         delta_y=event.y - self._drag_links_start_y,
                         canvas_obj=self._canvas_id_dict[self._drag_links_id])
        else:  # Canvas oder Kante => Canvas bewegen
            self._update(delta_x=event.x - self._drag_links_start_x,
                         delta_y=event.y - self._drag_links_start_y)
        self._drag_links_start_x = event.x
        self._drag_links_start_y = event.y

    def _drag_links_stop(self, event: tk.Event):
        self._maus_unten = None
        if not self.running:  # nicht, wenn gerade ein Algo läuft
            if self._drag_links_nur_click:  # es wurde nur links geklickt
                canvas_id = self._hole_canvas_id_bei_maus(event.x, event.y, (Knoten, Kante))
                if canvas_id is not None:
                    if self.selected2 is None or self.selected2.canvas_id != canvas_id:
                        if self.selected is None or self.selected.canvas_id != canvas_id:
                            self.selected = self._canvas_id_dict[canvas_id]
                        else:
                            self.selected = None
                    self.reset()
            else:  # es wurde mit links gezogen
                if self._drag_links_id is not None and isinstance(self._canvas_id_dict[self._drag_links_id], Knoten):
                    # ein Knoten wurde verschoben
                    self._update(delta_x=event.x - self._drag_links_start_x,
                                 delta_y=event.y - self._drag_links_start_y,
                                 canvas_obj=self._canvas_id_dict[self._drag_links_id])
                    kn_id = self._hole_canvas_id_bei_maus(event.x, event.y, (Knoten,))
                else:  # Canvas oder Kante wurde verschoben => Canvas schieben
                    if self._drag_links_start_x is not None and self._drag_links_start_y is not None:
                        self._update(delta_x=event.x - self._drag_links_start_x,
                                     delta_y=event.y - self._drag_links_start_y)
        self._drag_links_id = None
        self._drag_links_nur_click = True

    def _drag_rechts_start(self, event: tk.Event):
        self._maus_unten = "rechts"
        self._drag_rechts_nur_click = True
        if self.running: return  # nicht, wenn gerade ein Algo läuft
        self._drag_rechts_start_knoten_id = self._hole_canvas_id_bei_maus(event.x, event.y, (Knoten,))
        if self._drag_rechts_start_knoten_id is not None:
            kn = self._canvas_id_dict[self._drag_rechts_start_knoten_id]
            self._drag_rechts_start_x = kn.x
            self._drag_rechts_start_y = kn.y
            self._drag_rechts_temp_line = self.canvas.create_line(kn.x, kn.y, kn.x, kn.y,
                                                                  width=LINIEN_DICKE)

    def _drag_rechts_weiter(self, event: tk.Event):
        self._drag_rechts_nur_click = False
        if self.running: return  # nicht, wenn gerade ein Algo läuft
        if self._drag_rechts_start_knoten_id is not None:
            tmp_kn_id = self._hole_canvas_id_bei_maus(event.x, event.y, (Knoten,))
            if tmp_kn_id is None:
                # die Maus ist nicht auf einem Knoten => temp Kante von StartKn nach hier
                x = event.x
                y = event.y
            elif tmp_kn_id == self._drag_rechts_start_knoten_id:
                # die Maus ist auf dem StartKn → nichts machen
                return
            else:
                # die Maus ist auf einem anderen Knoten → temp Kante dort einrasten lassen
                tmp_kn = self._canvas_id_dict[tmp_kn_id]
                x = tmp_kn.x
                y = tmp_kn.y
            self.canvas.coords(self._drag_rechts_temp_line,
                               self._drag_rechts_start_x,
                               self._drag_rechts_start_y,
                               x, y)

    def _drag_rechts_stop(self, event: tk.Event):
        self._maus_unten = None
        if not self.running:  # nicht, wenn gerade ein Algo läuft
            if self._drag_rechts_nur_click:  # es wurde nur mit rechts geklickt → Knoten bauen oder Auswahl ändern
                canvas_id = self._hole_canvas_id_bei_maus(event.x, event.y, (Knoten, Kante))
                if canvas_id is None:  # neuen Knoten bauen
                    name = 1
                    while str(name) in self._knoten_dict:
                        name += 1
                    self._neuer_knoten(str(name), event.x, event.y)
                else:  # bisherige Auswahl ausmachen oder neue Anmachen
                    if self.selected is None or self.selected.canvas_id != canvas_id:
                        if self.selected2 is None or self.selected2.canvas_id != canvas_id:
                            self.selected2 = self._canvas_id_dict[canvas_id]
                        else:
                            self.selected2 = None
                    self.reset()
            else:  # es wurde mit rechts gezogen → evtl Kante verbinden
                if self._drag_rechts_start_knoten_id is None: return  # kein Startknoten gewählt
                tmp_kn_id = self._hole_canvas_id_bei_maus(event.x, event.y, (Knoten,))
                if tmp_kn_id is not None:  # ziel muss ein Knoten sein
                    if tmp_kn_id != self._drag_rechts_start_knoten_id:  # nicht zum selben Knoten
                        end_kn = self._canvas_id_dict[tmp_kn_id]
                        start_kn = self._canvas_id_dict[self._drag_rechts_start_knoten_id]
                        self._neue_kante(start_kn.name, end_kn.name)
                # dragging aufräumen
                self.canvas.delete(self._drag_rechts_temp_line)
        self._drag_rechts_temp_line = None
        self._drag_rechts_start_knoten_id = None

    def _pfeiltaste(self, dx: int = 0, dy: int = 0):
        if isinstance(self.selected, Knoten):
            self._update(delta_x=dx, delta_y=dy, canvas_obj=self.selected)

    def _pfeiltaste_hoch(self, event: tk.Event):
        self._pfeiltaste(dy=-1)

    def _pfeiltaste_links(self, event: tk.Event):
        self._pfeiltaste(dx=-1)

    def _pfeiltaste_rechts(self, event: tk.Event):
        self._pfeiltaste(dx=1)

    def _pfeiltaste_runter(self, event: tk.Event):
        self._pfeiltaste(dy=1)

    def _zoom(self, event: tk.Event):
        wert = 0
        match OS:
            case 'Linux':
                match event.num:
                    case 4:
                        wert = -1
                    case 5:
                        wert = 1
            case 'Windows':
                wert = -int((event.delta / 120))
            case 'Darwin':  # MacOS
                wert = -event.delta  # ungetestet
            case _:  # unbekanntes OS
                wert = event.delta  # kA, was hier hin muss

        # es soll relativ zum Mauszeiger gezoomt werden, also muss das Bild auch verschoben werden
        # (wenn man nur den zoom-Faktor ändert, zoomt man relativ zum Ursprung)
        if wert > 0:  # zoom raus (Bild verkleinern)
            self._update(delta_x=event.x, delta_y=event.y, delta_zoom=ZOOM_FAKTOR_RAUS)
        elif wert < 0:  # zoom rein (Bild vergrößern)
            self._update(delta_x=event.x, delta_y=event.y, delta_zoom=ZOOM_FAKTOR_REIN)

    ############################# optische Aktualisierungen ####################################################
    def reset(self):
        """
        stellt alle Knoten- und Kantenfarben auf default
        markierte Elemente (Start/Stop) bleiben hervorgehoben
        löscht die Algo-Ausgabe
        """
        for kn in self.knoten:
            if kn is self.selected:
                self.canvas.itemconfigure(kn.canvas_id, fill=FARBE_KNOTEN_MITTE, outline=FARBE_AUSWAHL)
            elif kn is self.selected2:
                self.canvas.itemconfigure(kn.canvas_id, fill=FARBE_KNOTEN_MITTE, outline=FARBE_AUSWAHL_2)
            else:
                self.canvas.itemconfigure(kn.canvas_id, fill=FARBE_KNOTEN_MITTE, outline=FARBE_KNOTEN_RAND)
        for ka in self.kanten:
            if ka is self.selected:
                self.canvas.itemconfigure(ka.canvas_id, fill=FARBE_AUSWAHL)
            elif ka is self.selected2:
                self.canvas.itemconfigure(ka.canvas_id, fill=FARBE_AUSWAHL_2)
            else:
                self.canvas.itemconfigure(ka.canvas_id, fill=FARBE_KANTEN)
        self._lbl_out.config(text="")

    def _update(self, delta_x: float = 0, delta_y: float = 0,
                delta_zoom: float | None = None,
                canvas_obj: Knoten | Kante | tuple | None = None):
        """
        Zeichnet Knoten und Kanten, mit optionalen Zoom- und Positionsupdates.
        canvas_obj ist entweder ein Element oder ein Tupel von Elementen

        ist canvas_obj angegeben wird/werden nur diese/s Element/e aktualisiert
        ist ein aktualisiertes Element ein Knoten, werden auch dessen Kanten aktualisiert
        ist canvas_obj nicht angegeben, wird alles aktualisiert

        ohne Zoomfaktor werden die aktualisierten Elemente um delta_x und delta_y verschoben.

        mit Zoomfaktor wird das Bild gezoomt und so verschoben, dass der Zoom relativ zur Maus stattfindet
        Dann müssen die Argumente delta_x und delta_y die Mausposition sein.
        """

        # Knoten und Kanten einsammeln
        if canvas_obj is None:  # nix angegeben => alles einsammeln
            knoten = {kn for kn in self.knoten}
            kanten = {ka for ka in self.kanten}
        else:  # zu ändernde Knoten und Kanten sammeln
            knoten = set()
            kanten = set()
            if not isinstance(canvas_obj, tuple): canvas_obj = (canvas_obj,)  # einzeln angegebenes Element in Tupel
            for elem in canvas_obj:
                if isinstance(elem, Knoten):
                    knoten.add(elem)
                elif isinstance(elem, Kante):
                    kanten.add(elem)
            for ka in self.kanten:  # Kanten die an geänderten Knoten hängen
                if ka.von in knoten or ka.nach in knoten: kanten.add(ka)

        if delta_zoom is None:
            for kn in knoten:
                kn.update(delta_x, delta_y)
        else:
            for kn in knoten:
                kn.update((delta_zoom - 1) * (kn.x - delta_x),
                          (delta_zoom - 1) * (kn.y - delta_y))
        multi_kanten = {ka.multi_kante for ka in kanten}  # statt Kanten Multi-Kanten aktualisieren
        for mk in multi_kanten:
            mk.update()

        self._lbl_knoten_zahl.config(text=f"Knoten\n{len(self._knoten_dict)}")
        self._lbl_kanten_zahl.config(text=f"Kanten\n{len(self._kanten_dict)}")

    def _update_out_label(self, text: str = None, weiter=True):
        if text is not None:
            self._algo_letzte = text
        if self.running:
            txt_neu = self._algo_letzte
            if weiter:
                txt_neu += f" ({'automatisch' if self._var_cb_auto.get() else '<weiter> für nächsten Schritt'})"
            self._lbl_out.config(text=txt_neu)
        else:
            self._lbl_out.config(text="")

    ################################# Algo Start/Weiter/Stop Logik ########################
    def _algo_auto_weiter(self):
        """
        Lässt einen laufenden Algorithmus automatisch einen weiteren Schritt machen.
        """
        if self._var_cb_auto.get() and self.running:
            self._algo_weiter()  # ein Schritt weiter
            self._fenster.after(ALGO_PAUSE_ZEIT, self._algo_auto_weiter)  # später nochmal

    def _algo_weiter(self):
        """
        Führt den nächsten Schritt eines laufenden Algos aus.
        Kann manuell (Button) oder automatisch (_algo_auto_weiter) getriggert werden.
        """
        try:
            x = next(self._algo_iter)
            if isinstance(x, tuple):
                self._update_out_label(x[0], False)
                self._algo_stop()
            else:
                self._update_out_label(x)
        except StopIteration:
            self._algo_stop()

    def _algo_start(self):
        """
        schaltet störende GUI ab und startet einen Algorithmus
        """
        if self._algo is not None:
            self.running = True
            self.reset()
            self._algo_iter = iter(self._algo())
            self._btn_startstop_toggle.config(text="stop")
            self._btn_speichern.config(state="disabled")
            self._btn_reset.config(state="disabled")
            self._btn_laden.config(state="disabled")

            if self._var_cb_auto.get():
                self._algo_auto_weiter()  # started die Schrittautomatik
            else:
                self._btn_algo_weiter.config(state="active")  # manuelles Schritt-Weiterschalten ermöglichen
                self._algo_weiter()  # ersten Schritt durchführen

    def _algo_stop(self):
        """
        beendet einen Algorithmus und stellt die GUI wieder auf normnal
        """
        self.running = False
        self._algo_iter = None
        self._btn_algo_weiter.config(state="disabled")
        self._btn_startstop_toggle.config(text="start")
        self._btn_reset.config(state="active")
        self._btn_speichern.config(state="active")
        self._btn_laden.config(state="active")

    def _cb_auto_toggle(self):
        self._update_out_label()  # Anzeige aktualisieren
        if self.running and self._var_cb_auto.get():
            self._fenster.after(ALGO_PAUSE_ZEIT, self._algo_auto_weiter)  # Automatik starten
        elif self.running:
            self._btn_algo_weiter.config(state="active")
        else:
            self._btn_algo_weiter.config(state="disabled")

        print(self._hintergrundbild_original)

    def _startstop_toggle(self):
        if self.running:
            self._algo_stop()
        else:
            self._algo_start()

    #################################################### Ende von Graph ###############################################


if __name__ == "__main__":
    # app = CanvasGraph(lade_graph="koenigsbergerbruecken.graph", multi_graph=True)
    app = Graph(lade_graph="graphen/Drachen.graph")
    print(app)

    print()

    print(*app.knoten)
    print(*app.kanten)

    app.starte_gui()

# todo
# built-in Hilfe
# undo / redo (create, delete, move)
