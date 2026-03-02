import canvas_graph as cg


class MeinGraph(cg.Graph):
    def __init__(self, **kwargs):
        cg.Graph.__init__(self, **kwargs)
        self.algo_hinzufuegen('alle Knoten iterieren', self.iteriere_knoten)

    def print_alle_knoten(self):
        [print(x) for x in self.knoten]

    def nachbarn(self, kn):
        ...


    def hole_nachbarn(self, kn: cg.Knoten):
        for ka in self.kanten:
            if kn is ka.von:
                yield ka.nach
            elif kn is ka.nach:
                yield ka.von

    def iteriere_knoten(self):
        for kn in self.knoten:
            # print(kn)
            self.canvas.itemconfig(kn.canvas_id, fill='yellow')
            yield f'Knoten {kn} markiert'
            self.canvas.itemconfig(kn.canvas_id, fill=cg.FARBE_KNOTEN_MITTE)
        yield "fertig", False

graph = MeinGraph()

# graph.lade_graph("graphen/laby2.graph")
# graph.lade_hintergrund_datei('graphen/laby2.png')


graph.lade_graph("graphen/Drachen.graph")
graph.starte_gui()
