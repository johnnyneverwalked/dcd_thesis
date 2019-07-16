import louvain
from igraph import Clustering
from random import sample

'''Dynamic Community Detection algorithm based on Aynaud-Guillaume et al 2010'''


def louvain_modified(snapshots, randomise_constraint=0.02):
    optimiser = louvain.Optimiser()
    partitions = []
    partition = None

    for i, snapshot in enumerate(snapshots):
        if partition is not None and randomise_constraint < 1:
            improv = 1
            optimiser_decay = 2

            partition = louvain.ModularityVertexPartition(snapshot.get_graph(),
                                                          init_clusters(snapshots[i].get_graph(),
                                                                        snapshots[i - 1].get_graph(),
                                                                        partition,
                                                                        randomise_constraint).membership)

            while improv > 0 and optimiser_decay > 0:
                improv = optimiser.optimise_partition(partition)
                if improv == 0:
                    optimiser_decay -= 1
                else:
                    optimiser_decay = 2
        else:
            partition = louvain.find_partition(snapshot.get_graph(), louvain.ModularityVertexPartition)
            snapshots[i].get_graph().vs["cluster_seed"] = partition.membership

        partitions.append(partition)

    return partitions


# returns a partition of graph1 based on a partition of graph2 and a constraint parameter
def init_clusters(graph1, graph2, partition, rand_percentage=0.0):
    if rand_percentage >= 1 or len(partition) == 0:
        return Clustering(list(range(len(graph1.vs))))

    for idx, cluster in enumerate(partition):
        if partition.size(idx) > 1:
            vertices = graph2.vs(cluster)["name"]
            graph1.vs(name_in=vertices)["cluster_seed"] = idx

    cluster_length = len(partition)

    for vertex in graph1.vs(cluster_seed=None):
        vertex["cluster_seed"] = cluster_length
        cluster_length += 1

    if rand_percentage > 0:
        vertices = graph1.vs(cluster_seed_lt=len(partition))
        random_vertices = round((len(vertices) - 1) * rand_percentage)
        for v in sample(range(0, len(vertices)), random_vertices):
            vertices[v]["cluster_seed"] = cluster_length
            cluster_length += 1
    return Clustering(graph1.vs["cluster_seed"])
