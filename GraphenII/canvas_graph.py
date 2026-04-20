import basis_graph
import tkinter as tk
import tkinter.filedialog as fd
from tkinter.ttk import Combobox
# from PIL import Image, ImageTk # wenn PIL installiert ist, können Bilder skaliert werden,
import os, platform, sys
from typing import Iterator, Callable, Literal, Generator
from math import sin, cos, pi

from queue import Queue
from collections import deque

q = Queue()


########################## Block mit Vorgabewerten, diese dürfen geändert werden ##########################
# Optik
LINIEN_DICKE = 4
KNOTEN_RADIUS = 15
PFEIL_FORM = (12, 25, 15)  # Länge der Spitze am Schaft, Länge Außenseite der Spitze, Länge Schaft/Außenecke
FARBE_SELECT1 = "lightgreen"  # Farbe ausgewählter Objekte erstes/Start/Anfang mit links click
FARBE_SELECT2 = "red"  # Farbe ausgewählter Objekte zweites/Ziel/Ende mit rechts click
FARBE_KANTEN_GEWICHTE = "black"
FARBE_KNOTEN_MITTE = "white"
FARBE_KNOTEN_TEXT = "black"
FARBE_KNOTEN_RAND = "black"
FARBE_KANTEN = "grey20"
FARBE_TEMP_LINIE = "black"  # die Kanten, während man sie hinzufügt
FORM_KNOTEN = 0  # 0 ○, 1 ▽, 2 □, 3 △, 4 ◇, ..., -1 ◁, -2 ▷, -3 nix, -4 ✧, -5 ☆, ...
FORM_KNOTEN_SELECT1 = 3  # Dreieck, Spitze oben
FORM_KNOTEN_SELECT2 = 1  # Dreieck Spitze unten

# Verhalten
ALGO_PAUSE_ZEIT = 1200  # Wartezeit in ms bei automatischer Ausführung von Algos
KLICK_DIST = 5  # wie weit man höchstens von Objekten entfernt klicken muss, um sie zu treffen
ZOOM_FAKTOR_REIN = 1.1  # wie stark/schnell der Zoom erfolgt
ZOOM_FAKTOR_RAUS = 1 / ZOOM_FAKTOR_REIN

######################## ab hier Finger weg (gucken ist natürlich erlaubt) #########################################

# Technik
OS = platform.system()  # "Linux", "Windows", "Darwin" (MacOS), andere?


##################################################### Knoten ######################################################

class Knoten(basis_graph.Knoten):
    def __init__(self, canvas: tk.Canvas,
                 name: str, x: float, y: float, r: float = KNOTEN_RADIUS,
                 kommentar: str | None = None,
                 anzahl_ecken: int = 0):
        basis_graph.Knoten.__init__(self, name, kommentar=kommentar)

        self._canvas: tk.Canvas = canvas
        self.x: float = x
        self.y: float = y
        self.r: float = r
        # self._anzahl_ecken = anzahl_ecken
        self._form: list[float] | None = None

        # font-Größe dynamisch anpassen, damit die Beschriftung in den Kreis passt
        font_size = int(2 * self.r)  # der Durchmesser des Kreises ist eine gute Obergrenze
        self.text_id: int = self._canvas.create_text(0, 0,
                                                     text=self.name,
                                                     font=('courier', font_size, "bold"),
                                                     fill=FARBE_KNOTEN_TEXT,
                                                     tags="Beschriftung")
        self.canvas_id: int = self._neues_canvas_knotensymbol(fill=FARBE_KNOTEN_MITTE, outline=FARBE_KNOTEN_RAND)
        self._canvas.tag_raise(self.text_id)

        while True:
            self._bbx1, self._bby1, self._bbx2, self._bby2 = self._canvas.bbox(self.text_id)
            if ((self._bbx2 - self._bbx1) < 2 * self.r - LINIEN_DICKE // 2 and
                    (self._bby2 - self._bby1) < 2 * self.r - LINIEN_DICKE // 2): break
            font_size -= 1
            self._canvas.itemconfigure(self.text_id, font=('courier', font_size, "bold"))
        self._text_off_x = self._text_off_y = LINIEN_DICKE // 2 - 2

    def _neues_canvas_knotensymbol(self, fill: str, outline: str):
        optionen = {"width": LINIEN_DICKE,
                    "tags": "Knoten",
                    "fill": fill,
                    "outline": outline}
        if self._form is None:  # Kreis
            cid = self._canvas.create_oval(-self.r, -self.r, self.r, self.r, **optionen)
        else:  # Polygon
            cid = self._canvas.create_polygon(self._form, **optionen)
        self._canvas.tag_raise(cid)  # Knoten oben
        self._canvas.tag_raise(self.text_id)  # Text über Knoten
        return cid

    @property
    def anzahl_ecken(self):
        return 0 if self._form is None else len(self._form) // 2

    def __set_design(self,  # die Methode soll nur vom Graph, aber nicht aus dem Graphtool aufgerufen werden
                     form: int | None = None,
                     fill: str | None = None,
                     outline: str | None = None) -> int:
        """
        :ecken: legt die Form der Kreisdarstellung fest
         # 0 ○, 1 ▽, 2 □, 3 △, 4 ◇, ..., -1 ◁, -2 ▷, -3 nix, -4 ✧, -5 ☆, ...
         3 und höher: entsprechende n-Ecke mit Spitze oben
         2 Quadrat
         1 Dreieck Spitze unten
         0 Kreis
         -1 Dreieck Spitze links
         -2 Dreieck Spitze rechts
         -3 und tiefer: Sterne mit entsprechend vielen Zacken

        Ist die bisherige Form schon die gewünschte, tut es nichts.
        Ist die Anzahl anders, wird die bisherige shape/form des Knotens gelöscht und eine neue angelegt (neue ID!).

        Das muss vom Graph aufgerufen werden, nicht von wo anders außerhalb!
        Der aufrufende Graph muss seine Datenstrukturen an die neue ID anpassen!

        :fill: und :outline: siehe canvas

        :return: die bestehende (bei gleicher Anzahl) oder die neue Canvas-ID (bei neuer Anzahl)
        """
        if (form is None
                or form == 0 and self._form is None  # war Kreis → bleibt, wie es ist
                or self._form is not None and len(self._form) == form  # war Polygon → bleibt, wie es ist
        ):
            # nur Farben ändern
            optionen = {}
            if fill is not None: optionen["fill"] = fill
            if outline is not None: optionen["outline"] = outline
            if optionen: self._canvas.itemconfigure(self.canvas_id, **optionen)
        else:
            if not isinstance(form, int): raise TypeError("form muss ein int oder None sein")
            # (auch) Form ändern
            if form == 0:  # soll Kreis werden
                self._form = None
            elif form > -3:  # soll n-Eck Polygon werden
                if form < 2:  # die 0 ist schon ausgeschlossen, -1, -2 und 1 sind Dreiecke
                    ecken = 3
                elif form == 2:
                    ecken = 4
                else:
                    ecken = form
                self._form = []
                match form:
                    case 2:
                        bogen = pi / 4  # Quadrat gerade → erste Spitze oben rechts, also oben flach
                    case 1:
                        bogen = 1.5 * pi  # Dreieck, erste Spitze unten
                    case -1:
                        bogen = pi  # Dreieck, erste Spitze links
                    case -2:
                        bogen = 0  # Dreieck, erste Spitze rechts
                    case _:
                        bogen = pi / 2  # alle n-Ecke ab 3, jeweils erste Spitze oben
                w = 2 * pi / ecken
                for i in range(ecken):
                    l = KNOTEN_RADIUS + LINIEN_DICKE
                    self._form.append(cos(bogen) * l)
                    self._form.append(-sin(bogen) * l)
                    bogen += w
            else:  # kleiner -2 -> -n-zackiger Stern
                ecken = -form
                self._form = []
                bogen = pi / 2
                w = pi / ecken
                l1 = (1.3 + 1 / ecken) * KNOTEN_RADIUS  # Stern Zacke nach außen
                l2 = (0.75 - 2 / ecken ** 2) * KNOTEN_RADIUS  # Stern Zacke nach innen
                for i in range(ecken):
                    self._form.append(cos(bogen) * l1)
                    self._form.append(-sin(bogen) * l1)
                    bogen += w
                    self._form.append(cos(bogen) * l2)
                    self._form.append(-sin(bogen) * l2)
                    bogen += w
            fill = self._canvas.itemcget(self.canvas_id, "fill") if fill is None else fill
            outline = self._canvas.itemcget(self.canvas_id, "outline") if outline is None else outline
            self._canvas.delete(self.canvas_id)
            self.canvas_id = self._neues_canvas_knotensymbol(fill=fill, outline=outline)
        return self.canvas_id

    def update(self, delta_x: float = 0, delta_y: float = 0):
        self.x += delta_x
        self.y += delta_y
        if self._form is None:
            self._canvas.coords(self.canvas_id, self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r)
        else:
            self._canvas.coords(self.canvas_id, [p + (self.y if i % 2 else self.x) for i, p in enumerate(self._form)])
        self._canvas.coords(self.text_id, self.x + self._text_off_x, self.y + self._text_off_y)


########################################## Ende von Knoten #############################################

################################################ Kante #############################################
class Kante(basis_graph.Kante):
    """
    Kanten werden nicht direkt auf den Canvas gezeichnet, sondern einer MultiKante zugeordnet.
    Es gibt pro Kante ein Knotenpaar und pro Knotenpaar genau eine MultiKante.
    Es gibt also pro MultiKante eine oder mehrere Kanten am betreffenden Knotenpaar
    (Mehrere sind es bei gerichteten Kanten in verschiedene Richtungen oder bei Mehrfachkanten.)
    Eine Kante delegiert alle Zeichenoperationen an ihre MultiKante, diese zeichnet alle ihre Kanten gemeinsam.
    """

    def __init__(self, canvas: tk.Canvas, name: str, von: Knoten, nach: Knoten,
                 multi_kante: "_CanvasMultiKante",
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
                                                  tags="Kante",
                                                  width=LINIEN_DICKE,
                                                  fill=FARBE_KANTEN,
                                                  **line_args)
        if self.gewicht is None:
            self.text_id = None
        else:
            self.text_id = self._canvas.create_text(0, 0,
                                                    text=str(self.gewicht),
                                                    font=('courier', PFEIL_FORM[2] * 2, "bold"),
                                                    fill=FARBE_KANTEN_GEWICHTE,
                                                    tags="Beschriftung")

    @property
    def nach(self) -> Knoten:
        return self.__nach

    @property
    def von(self) -> Knoten:
        return self.__von

    def __set_design(self,  # die Methode soll nur vom Graph, aber nicht aus dem Graphtool aufgerufen werden
                     fill: str | None = None,
                     dash: tuple[int, ...] | None = None):
        """
        setzt Farbe (fill) und Strichelung (dash) der Kante
        """
        optionen = {}
        if fill is not None: optionen["fill"] = fill
        if dash is not None: optionen["dash"] = dash
        if optionen: self._canvas.itemconfigure(self.canvas_id, **optionen)


############################################# Ende von Kante #############################################

############################################# CanvasMultiKante ##########################################

class _CanvasMultiKante:
    """
    Eine CanvasMultiKante bildet alle Kanten zwischen zwei Knoten ab.
    Es ist egal, ob die Kanten gerichtet sind oder nicht oder ob Mehrfachkanten dabei sind.
    Es gibt zwischen zwei Knoten höchstens eine solche MultiKante auf dem Canvas (Richtung und Anzahl egal).
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
        - rechts klicken auf Knoten oder Kante → markieren/un-markieren Letzter/Ende/Ziel
        - rechts klicken auf Canvas → neuer Knoten
        - Knoten mit links ziehen → Knoten bewegen
        - Knoten mit rechts ziehen → neue Kante einbauen ab diesem Knoten, muss auf anderem Knoten losgelassen werden
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
        self._knoten_set: set = set()  # intern unnötig, wird nur für schnelle Zugriffe immer aktuell vorgehalten
        self._kanten_dict: dict[str, Kante] = {}
        self._kanten_set: set = set()  # intern unnötig, wird nur für schnelle Zugriffe immer aktuell vorgehalten
        self._multi_kanten_dict: dict[str, _CanvasMultiKante] = {}
        self._canvas_id_dict: dict[int, Knoten | Kante] = {}

        self._click_obj_links: Knoten | Kante | None = None  # das geklickte Ding
        self._click_obj_rechts: Knoten | None = None  # das geklickte Ding - immer der Startknoten für neue Kante
        self._drag_nur_click_links: bool = True  # ob ein nur geklickt oder schon bewegt wurde
        self._drag_nur_click_rechts: bool = True  # ob ein nur geklickt oder schon bewegt wurde
        self._drag_start_links_x: float | None = None
        self._drag_start_links_y: float | None = None
        self._drag_start_rechts_x: float | None = None
        self._drag_start_rechts_y: float | None = None
        self._drag_rechts_temp_line_id: int | None = None  # temporäre ID der neu anzulegenden Kante

        self._fenster = tk.Tk()
        self._fenster.geometry("1220x720")

        self.canvas = tk.Canvas(master=self._fenster)
        self.canvas.pack(side="bottom", expand=True, fill="both")

        # self._hintergrundbild_original: Image.Image | None = None           # mit PIL statt der nächsten Zeile
        self._hintergrundbild_original: tk.PhotoImage | None = None
        # self._hintergrundbild_resized: ImageTk.PhotoImage | None = None     # mit PIL diese Zeile zusätzlich
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
        self.selected1: Knoten | Kante | None = None  # das auf dem Canvas gewählte Ding (Kante oder Knoten)
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
        self._btn_reset = tk.Button(master=frm_btns_algo, text="Optik-Reset", command=self.reset)
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

        self.canvas.bind('<ButtonPress-1>', self._drag_start_links)
        self.canvas.bind('<B1-Motion>', self._drag_links_weiter)
        self.canvas.bind('<ButtonRelease-1>', self._drag_links_stop)

        self.canvas.bind('<ButtonPress-3>', self._drag_start_rechts)
        self.canvas.bind('<B3-Motion>', self._drag_rechts_weiter)
        self.canvas.bind('<ButtonRelease-3>', self._drag_rechts_stop)

        self._fenster.bind('<Delete>', self._delete)
        self._fenster.bind('<Up>', self._pfeiltaste_hoch)
        self._fenster.bind('<Left>', self._pfeiltaste_links)
        self._fenster.bind('<Right>', self._pfeiltaste_rechts)
        self._fenster.bind('<Down>', self._pfeiltaste_runter)

        self.canvas.bind('<Configure>', self._canvas_config)  # für Größenänderung

        self._combo_algos.bind('<<ComboboxSelected>>', self._combo_select)

        # los gehts
        if lade_graph is not None:
            self.lade_graph(lade_graph)

    def __str__(self):
        return (f"{basis_graph.Graph.__str__(self)}\n"
                f"Auswahl 1: {'nix' if self.selected1 is None else self.selected1}, "
                f"Auswahl 2: {'nix' if self.selected2 is None else self.selected2}")

    @property  # basis_graph property überschreiben
    def kanten(self) -> set[Kante]:
        return self._kanten_set

    @property  # basis_graph property überschreiben
    def knoten(self) -> set[Knoten]:
        return self._knoten_set

    ################### Methoden (außer Properties, Callbacks und Algo-Logik) ##################################

    def algo_hinzufuegen(self, name: str, funktion: Callable):
        self._algo_dict[name] = funktion
        self._combo_algos['values'] = (*self._combo_algos['values'], name)

    def _graph_speichern(self):
        if self.running: return  # nicht, wenn gerade ein Algo läuft
        dateiname = fd.asksaveasfilename(initialdir=os.path.realpath(__file__),
                                         filetypes=(("Graph Datei", "*.grf *.graph"),),
                                         defaultextension=".graph")
        if dateiname:
            with open(dateiname, "wt") as datei:
                elem: str | Knoten | Kante
                for elem in self._datei_zeilen:
                    if (t := type(elem)) == str:
                        datei.write(f"{elem}")
                        if not elem.endswith('\n'): datei.write('\n')
                    elif t == Knoten:
                        datei.write(f"{elem.name};{int(elem.x)};{int(elem.y)}"
                                    f"{"\n" if elem.kommentar is None else f' #{elem.kommentar}'}")
                    elif t == Kante:
                        datei.write(f"{elem.von.name},{elem.nach.name}"
                                    f"{f',{int(elem.gewicht)}' if self.ist_gewichtet else ''}"
                                    f"{"\n" if elem.kommentar is None else f' #{elem.kommentar}'}")

    def _hole_canvas_obj_bei_maus(self, x: float, y: float, typen: tuple) -> Knoten | Kante | None:
        canvas_ids = self.canvas.find_overlapping(x - KLICK_DIST, y - KLICK_DIST, x + KLICK_DIST, y + KLICK_DIST)
        for c_id in canvas_ids:
            if c_id in self._canvas_id_dict:
                if type(c_obj := self._canvas_id_dict[c_id]) in typen: return c_obj
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
                self.selected1 = None
                self.selected2 = None
                self._knoten_set.clear()
                self._kanten_set.clear()

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
            self.lade_graph(dateiname)
            print(f"{dateiname} geladen")

    def _lade_hintergrund(self):
        if self._hintergrundbild_original is not None:
            # x = self.canvas.winfo_width() # mit PIL diese Zeile zusätzlich
            # y = self.canvas.winfo_height() # mit PIL diese Zeile zusätzlich
            # resized = self._hintergrundbild_original.resize((x, y)) # mit PIL diese Zeile zusätzlich
            # self._hintergrundbild_resized = ImageTk.PhotoImage(resized) # mit PIL diese Zeile zusätzlich
            if self._canvas_background_id is None or self._canvas_background_id not in self.canvas.find_all():
                # mit PIL statt der nächsten Zeile
                # self._canvas_background = self.canvas.create_image(0, 0, image=self._hintergrundbild_resized, anchor="nw")
                self._canvas_background_id = self.canvas.create_image(0, 0,
                                                                      image=self._hintergrundbild_original,
                                                                      anchor="nw",
                                                                      tags="Hintergrund")
                self.canvas.tag_lower(self._canvas_background_id)
            else:
                # mit PIL statt der nächsten Zeile
                # self.canvas.itemconfigure(self._canvas_background, image=self._hintergrundbild_resized)
                self.canvas.itemconfigure(self._canvas_background_id, image=self._hintergrundbild_original)

    def lade_hintergrund_datei(self, bilddatei: str):
        try:
            # mit PIL statt der nächsten Zeile
            # self._hintergrundbild_original = Image.open(bilddatei)
            self._hintergrundbild_original = tk.PhotoImage(file=bilddatei)
        except Exception as e:
            print(e, e.args)

    def _neuer_knoten(self, name: str, x: int, y: int, kommentar: str | None = None, insert: bool = True):
        if self.running: return  # nicht, wenn gerade ein Algo läuft
        kn = Knoten(self.canvas, name, int(x), int(y), kommentar=kommentar)
        self._knoten_dict[name] = kn
        self._canvas_id_dict[kn.canvas_id] = kn
        self._knoten_set.add(kn)

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
            mk = _CanvasMultiKante(self.canvas, base_name, k_von, k_nach)
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
        self._kanten_set.add(ka)
        self._datei_zeilen.append(ka)
        self._update(canvas_obj=ka)

    def starte_gui(self):
        self._fenster.mainloop()

    ###################################### GUI Callbacks ###########################################################

    def _canvas_config(self, event: tk.Event):  # insbesondere die Größenänderung
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
        if self.selected1 is None: return
        if isinstance(self.selected1, Kante):
            self._multi_kanten_dict[self.selected1.multi_kante.name].entferne_kante(self.selected1.name)
            del self._kanten_dict[self.selected1.name]
        elif isinstance(self.selected1, Knoten):
            for ka in self.kanten:  # Knoten mit Kanten kann man nicht löschen
                if ka.von is self.selected1 or ka.nach is self.selected1:
                    print(f"Knoten {self.selected1} hat noch Kanten (z.B. {ka}) => wird nicht gelöscht")
                    return
            del self._knoten_dict[self.selected1.name]
        else:  # hier sind nur Knoten oder Kanten auswählbar, aber falls doch.....
            return
        if self.selected1.text_id is not None: self.canvas.delete(self.selected1.text_id)
        self._datei_zeilen.remove(self.selected1)
        del self._canvas_id_dict[self.selected1.canvas_id]
        self.canvas.delete(self.selected1.canvas_id)
        self.selected1 = None
        self._knoten_set = set(self._knoten_dict.values())
        self._kanten_set = set(self._kanten_dict.values())
        self._update_status_label()  # self.reset() wäre overkill

    def _drag_start_links(self, event: tk.Event):
        self._maus_unten = "links"
        self._drag_start_links_x = event.x
        self._drag_start_links_y = event.y
        self._click_obj_links = self._hole_canvas_obj_bei_maus(event.x, event.y, (Knoten, Kante))
        self._drag_nur_click_links = True

    def _drag_start_rechts(self, event: tk.Event):
        self._maus_unten = "rechts"
        self._drag_nur_click_rechts = True
        if self.running: return  # nicht, wenn gerade ein Algo läuft (rechts-Klicks sind Änderungen)
        self._click_obj_rechts = self._hole_canvas_obj_bei_maus(event.x, event.y, (Knoten,))
        if self._click_obj_rechts is not None:  # es ist immer ein Knoten, hier beginnt eine neue temp-Linie
            # die temp-Linie wird am Ende auf jeden Fall wieder entfernt
            # sollte die temp-Linie auf einem Ziel-Knoten landen, wird dort eine "richtige" neue Kante gebaut
            kn = self._click_obj_rechts
            self._drag_start_rechts_x = kn.x  # damit die temp-Linie am Knoten und nicht an der Maus losgeht
            self._drag_start_rechts_y = kn.y  # damit die temp-Linie am Knoten und nicht an der Maus losgeht
            self._drag_rechts_temp_line_id = self.canvas.create_line(kn.x, kn.y, kn.x, kn.y,
                                                                     width=LINIEN_DICKE,
                                                                     fill=FARBE_TEMP_LINIE)  # die temp-Linie

    def _drag_links_weiter(self, event: tk.Event):
        self._drag_nur_click_links = False
        if self._click_obj_links is not None and isinstance(self._click_obj_links, Knoten):
            # Knoten => bewegen
            self._update(delta_x=event.x - self._drag_start_links_x,
                         delta_y=event.y - self._drag_start_links_y,
                         canvas_obj=self._click_obj_links)
        else:  # Canvas oder Kante oder was anderes => Canvas bewegen (also alles AUF dem Canvas bewegen)
            self._update(delta_x=event.x - self._drag_start_links_x,
                         delta_y=event.y - self._drag_start_links_y)
        self._drag_start_links_x = event.x
        self._drag_start_links_y = event.y

    def _drag_rechts_weiter(self, event: tk.Event):
        self._drag_nur_click_rechts = False
        if not self.running and self._click_obj_rechts is not None:  # wenn kein Algo läuft und etwas angeklickt wurde
            tmp_kn = self._hole_canvas_obj_bei_maus(event.x, event.y, (Knoten,))
            if tmp_kn is not self._click_obj_rechts:  # nichts machen, wenn Maus auf StartKn
                if tmp_kn is None:  # die Maus ist nicht auf einem Knoten => temp Linie von StartKn nach hier
                    x = event.x
                    y = event.y
                else:  # die Maus ist auf einem anderen Knoten → temp Kante dort einrasten lassen
                    x = tmp_kn.x
                    y = tmp_kn.y
                self.canvas.coords(self._drag_rechts_temp_line_id,
                                   self._drag_start_rechts_x, self._drag_start_rechts_y,
                                   x, y)

    def _drag_links_stop(self, event: tk.Event):
        """
        Das Bewegen von Knoten und Canvas macht schon _drag_links_weiter.
        Hier wird nur noch die (Un-)Markierung von selected1 gemacht.
        """
        if (
                not self.running  # nicht an/abwählen, wenn Algo läuft
                and self._drag_nur_click_links  # es wurde nur geklickt, nicht gezogen
                and self._click_obj_links is not None  # nicht, wenn nichts angeklickt wurde
        ):
            self.knoten_kante_geklickt(self._click_obj_links)
        self._maus_unten = None
        self._click_id_links = None

    def _drag_rechts_stop(self, event: tk.Event):
        """
        Das Bewegen der tmp-Linie _drag_rechts_weiter.
        Hier wird "nur noch" ggf gemacht:
        - (Un-)Markierung von selected2
        - Anlegen neuer Knoten/Kanten
        """
        self._maus_unten = None
        self.canvas.delete(self._drag_rechts_temp_line_id)
        self._drag_rechts_temp_line_id = None
        if not self.running:  # nicht, wenn gerade ein Algo läuft (aufräumen und beenden)
            if self._drag_nur_click_rechts:  # es wurde nur geklickt, nicht gezogen → Knoten bauen oder Auswahl ändern
                c_obj = self._hole_canvas_obj_bei_maus(event.x, event.y, (Knoten, Kante))
                if c_obj is None:  # leere Stelle → neuen Knoten bauen
                    name = 1
                    while str(name) in self._knoten_dict:
                        name += 1
                    self._neuer_knoten(str(name), event.x, event.y)
                else:  # bisherige Auswahl ausmachen oder neue Anmachen
                    self.knoten_kante_geklickt(c_obj, False)
            else:  # es wurde mit rechts gezogen → evtl. neue Kante bauen
                if self._click_obj_rechts is not None:  # es muss ein Startknoten gewählt sein
                    end_kn = self._hole_canvas_obj_bei_maus(event.x, event.y, (Knoten,))
                    if end_kn is not None and end_kn is not self._click_obj_rechts:  # Ziel muss ein ANDERER Knoten sein
                        self._neue_kante(self._click_obj_rechts.name, end_kn.name)
        self._click_id_rechts = None

    def _pfeiltaste(self, dx: int = 0, dy: int = 0):
        if isinstance(self.selected1, Knoten):
            self._update(delta_x=dx, delta_y=dy, canvas_obj=self.selected1)

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

    def knoten_kante_geklickt(self,
                              k: Knoten | Kante,
                              links: bool = True):
        """
        wenn ein Knoten oder eine Kante geklickt wird, muss evtl selected und selected2 neu belegt und gemalt werden

        :k: der/die zu wählende Knoten/Kante
        :links: ob mit links geklickt wurde (sonst ist es rechts)
        bei Bedarf werden alte und neue Auswahlen neu designt und gemalt
        """

        def an(k: Knoten | Kante):
            if isinstance(k, Knoten):
                self.knoten_design(k,
                                   form=(1, 3)[links],
                                   rand=(FARBE_SELECT2, FARBE_SELECT1)[links],
                                   mitte=FARBE_KNOTEN_MITTE)
                # knoten_id_wechsel(k, form=(1, 3)[links], outline=(FARBE_SELECT2, FARBE_SELECT1)[links])
            elif isinstance(k, Kante):
                self.kanten_design(k, farbe=(FARBE_SELECT2, FARBE_SELECT1)[links])

        def aus(k: Knoten | Kante):
            if isinstance(k, Knoten):
                self.knoten_design(k,
                                   form=FORM_KNOTEN,
                                   rand=FARBE_KNOTEN_RAND,
                                   mitte=FARBE_KNOTEN_MITTE)
            elif isinstance(k, Kante):
                self.kanten_design(k, farbe=FARBE_KANTEN)

        if k is None: return  # nur wenn da was ist
        if links and k is self.selected2: return  # k kann nicht beides sein
        if not links and k is self.selected1: return  # k kann nicht beides sein

        if links and k is self.selected1:  # bestehendes selected wird ausgeschaltet
            aus(k)
            self.selected1 = None
            self._update(canvas_obj=k)
        elif not links and k is self.selected2:  # bestehendes selected2 wird ausgeschaltet
            aus(k)
            self.selected2 = None
            self._update(canvas_obj=k)
        elif links and self.selected1 is None:  # es gibt kein selected und es wird eins gewählt
            an(k)
            self.selected1 = k
            self._update(canvas_obj=k)
        elif not links and self.selected2 is None:  # es gibt kein selected2 und es wird eins gewählt
            an(k)
            self.selected2 = k
            self._update(canvas_obj=k)
        elif links:  # selected wird umgeschaltet (das Alte muss aus, das Neue an)
            k_alt = self.selected1
            aus(k_alt)
            an(k)
            self.selected1 = k
            self._update(canvas_obj=(k, k_alt))
        elif not links:  # selected2 wird umgeschaltet (das Alte muss aus, das Neue an)
            k_alt = self.selected2
            aus(k_alt)
            an(k)
            self.selected2 = k
            self._update(canvas_obj=(k, k_alt))

    def kanten_design(self, ka: Kante | None,
                      *,  # ab hier nur benannt
                      farbe: str | None = None,
                      striche: tuple = ()):
        if ka is not None:
            # hier ruft der Graph eine Methode auf, die nicht aus dem Graphtool aufgerufen werden soll → name mangling
            ka._Kante__set_design(fill=farbe, dash=striche)
            self._update(canvas_obj=ka)

    def knoten_design(self,
                      kn: Knoten | None,
                      *,  # ab hier nur benannt
                      form: int = None,
                      rand: str | None = None,
                      mitte: str | None = None):
        """
        legt die Form und Farbe der Kreisdarstellung fest
        0 Ecken → Kreis
        1 Ecke → Dreieck Spitze unten
        2 Ecken → Quadrat (mit einer Seite oben)
        ab 3 Ecken → n-Eck Spitze oben (Dreieck, Quadrat, ...)
        """
        if kn is not None:
            alte_id = kn.canvas_id
            # hier ruft der Graph eine Methode auf, die nicht aus dem Graphtool aufgerufen werden soll → name mangling
            neue_id = kn._Knoten__set_design(form=form,
                                             # bei Bedarf wird das CanvasObj-neu hier gebaut und alt gelöscht
                                             fill=mitte,
                                             outline=rand)
            if alte_id != neue_id:
                del self._canvas_id_dict[alte_id]
                kn.canvas_id = neue_id
                self._canvas_id_dict[neue_id] = kn

            self._update(canvas_obj=kn)

    def reset(self):
        """
        stellt alle Knoten- und Kantenfarben auf default
        markierte Elemente (Start/Stop) bleiben hervorgehoben
        löscht die Algo-Ausgabe
        """
        for kn in self.knoten:
            if kn is self.selected1:
                self.knoten_design(kn, form=FORM_KNOTEN_SELECT1, mitte=FARBE_KNOTEN_MITTE,
                                   rand=FARBE_SELECT1)
            elif kn is self.selected2:
                self.knoten_design(kn, form=FORM_KNOTEN_SELECT2, mitte=FARBE_KNOTEN_MITTE,
                                   rand=FARBE_SELECT2)
            else:
                self.knoten_design(kn, form=FORM_KNOTEN, mitte=FARBE_KNOTEN_MITTE, rand=FARBE_KNOTEN_RAND)
        for ka in self.kanten:
            if ka is self.selected1:
                self.kanten_design(ka, farbe=FARBE_SELECT1)
            elif ka is self.selected2:
                self.kanten_design(ka, farbe=FARBE_SELECT2)
            else:
                self.kanten_design(ka, farbe=FARBE_KANTEN)
        self._lbl_out.config(text="")

    def _update(self, delta_x: float = 0, delta_y: float = 0,
                delta_zoom: float | None = None,
                canvas_obj: Knoten | Kante | tuple[Knoten | Kante | None, ...] | None = None):
        """
        Zeichnet Knoten und Kanten, mit optionalen Zoom- und Positionsupdates.
        canvas_obj ist entweder ein Element oder ein Tupel von Elementen

        Ist canvas_obj angegeben wird/werden nur diese/s Element/e aktualisiert.
        Ist ein aktualisiertes Element ein Knoten, werden auch dessen Kanten aktualisiert.
        Ist canvas_obj nicht angegeben, wird alles aktualisiert.

        Ohne Zoomfaktor werden die aktualisierten Elemente um delta_x und delta_y verschoben.

        Mit Zoomfaktor wird das Bild gezoomt und so verschoben, dass der Zoom relativ zur Maus stattfindet.
        Dann müssen die Argumente delta_x und delta_y die Mausposition sein.
        """

        # Knoten und Kanten einsammeln
        if canvas_obj is None:  # nichts angegeben → alles einsammeln
            knoten = {kn for kn in self.knoten}
            kanten = {ka for ka in self.kanten}
        else:  # zu ändernde Knoten und Kanten sammeln
            knoten = set()
            kanten = set()
            if not isinstance(canvas_obj, tuple): canvas_obj = (canvas_obj,)  # einzelnes Element in Tupel packen
            for elem in canvas_obj:  # Tupel auswerten
                if isinstance(elem, Knoten):
                    knoten.add(elem)
                elif isinstance(elem, Kante):
                    kanten.add(elem)
            for ka in self.kanten:  # Kanten, die an geänderten Knoten hängen, auch einsammeln
                if ka.von in knoten or ka.nach in knoten: kanten.add(ka)

        if delta_zoom is None:  # nur alles verschieben
            for kn in knoten:
                kn.update(delta_x, delta_y)
        else:  # zoom mit reinrechnen
            for kn in knoten:
                kn.update((delta_zoom - 1) * (kn.x - delta_x),
                          (delta_zoom - 1) * (kn.y - delta_y))

        # statt Kanten werden Multi-Kanten aktualisiert
        multi_kanten = {ka.multi_kante for ka in kanten}
        for mk in multi_kanten:
            mk.update()

        # bei der Gelegenheit gleich noch die Anzeigelabel aktualisieren
        self._update_status_label()

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

    def _update_status_label(self):
        self._lbl_knoten_zahl.config(text=f"Knoten\n{len(self._knoten_dict)}")
        self._lbl_kanten_zahl.config(text=f"Kanten\n{len(self._kanten_dict)}")

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
        beendet einen Algorithmus und stellt die GUI wieder auf normal
        """
        self.running = False
        self._algo_iter = None
        self._btn_algo_weiter.config(state="disabled")
        self._btn_startstop_toggle.config(text="start")
        self._btn_reset.config(state="active")
        self._btn_speichern.config(state="active")
        self._btn_laden.config(state="active")

    def _cb_auto_toggle(self):
        if self.running and self._var_cb_auto.get():
            self._fenster.after(ALGO_PAUSE_ZEIT, self._algo_auto_weiter)  # Automatik starten
        elif self.running:
            self._btn_algo_weiter.config(state="active")
        else:
            self._btn_algo_weiter.config(state="disabled")
        self._update_out_label()  # Anzeige aktualisieren

    def _startstop_toggle(self):
        if self.running:
            self._algo_stop()
        else:
            self._algo_start()

    #################################################### Ende von Graph ###############################################


if __name__ == "__main__":
    # app = CanvasGraph(lade_graph="graphen/Königsberg.graph", multi_graph=True)
    app = Graph(lade_graph="graphen/Drachen.graph")
    app.starte_gui()

# todo
# built-in Hilfe
# undo / redo (create, delete, move)
# mögliche Bedeutung des zweiten Parameters eines yield: z.B. wartezeit (in ms, 0 heißt automatik aus, -1 heißt Ende)
