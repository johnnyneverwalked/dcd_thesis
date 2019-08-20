from igraph import *
import louvain


def ms_sum(fname, weight="interaction"):
    sum_graph = Graph().Read_Pickle(fname)
    communities = louvain.find_partition(sum_graph, louvain.ModularityVertexPartition, weights=weight)

    return communities.quality()


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


