from igraph import *
import louvain


def ms_sum(fname, weight="month"):
    sum_graph = Graph().Read_Pickle(fname)
    communities = louvain.find_partition(sum_graph, louvain.ModularityVertexPartition, weights=weight)
    # remove singleton communities
    communities = list(filter(lambda c: len(c) > 1, communities))

    return communities


def ms_avg(snapshots, weights={}):
    if not snapshots:
        return None

    optimiser = louvain.Optimiser()

    static_modularities = [0 for s in snapshots]
    partitions = [louvain.ModularityVertexPartition(snap.get_graph()) for snap in snapshots]
    partitions_agg = [partition.aggregate_partition() for partition in partitions]

    for idx, snap in enumerate(snapshots):
        try:
            weights[idx]
        except KeyError:
            weights[idx] = 1

    improv = 1
    while improv > 0:
        improv = 0

        # phase 1
        for idx in range(len(partitions_agg)):
            if optimiser.move_nodes(partitions_agg[idx]) > 0:
                improv = 1
            static_modularities[idx] = partitions_agg[idx].quality()

        # phase 2
        if improv > 0:
            for idx in range(len(partitions_agg)):
                partitions[idx].from_coarse_partition(partitions_agg[idx])
                partitions_agg[idx] = partitions_agg[idx].aggregate_partition()

    return (sum([static_modularities[idx] * weights[idx] for idx in range(len(static_modularities))])
            / sum(weights.values()))


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
