from datetime import date
from igraph import *


class Snapshot:

    def __init__(self, month, file, loops=False, no_zero_degree=True):
        self._graph = Graph()

        vertices = set()
        edges = []

        with open(file, 'r') as enron:
            for line in enron:
                tokens = line.split(" ")
                if date.fromtimestamp(int(tokens[3])).month == month:
                    vertices.add(tokens[0])
                    vertices.add(tokens[1])

                    if tokens[0] != tokens[1] or loops:
                        edges.append((tokens[0], tokens[1]))

        self._graph.add_vertices(list(vertices))
        self._graph.add_edges(edges)
        if no_zero_degree:
            self._graph.delete_vertices(self._graph.vs(_degree=0))

    def get_graph(self):
        return self._graph

    def get_vertices(self, community):
        return self._graph.vs(community)["name"]

    def summary(self):
        summary(self._graph)
