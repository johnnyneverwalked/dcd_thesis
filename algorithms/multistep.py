from igraph import *
import louvain


def ms_sum(fname, weight="month"):
    sum_graph = Graph().Read_Pickle(fname)
    print(sum_graph.summary())
    communities = louvain.find_partition(sum_graph, louvain.ModularityVertexPartition, weights=weight)
    communities = list(filter(lambda c: len(c) > 1, communities))

    return communities


# builds the a sum_graph from given snapshots and saves it to a pickle file
def build_sum_graph(snapshots, weight="month", fname="sumGraph.pkl"):
    sum_graph = Graph()
    for idx, snapshot in enumerate(snapshots):
        if idx == 0:
            sum_graph = snapshot.get_graph()
            sum_graph.es()[weight] = 1
            continue
        sum_graph.add_vertices(list(set(snapshot.get_graph().vs()["name"]) - set(sum_graph.vs()["name"])))
        sum_graph.add_edges([e.tuple for e in snapshot.get_graph().es()])
        sum_graph.es(lambda e: e[weight] is None)[weight] = idx + 1

    sum_graph.simplify(combine_edges={weight: edge_duration})
    sum_graph.write_pickle(fname=fname)


def edge_duration(iterable):
    return max(iterable) - min(iterable) + 1
