from algorithms.takaffoli import takaffoli
from algorithms.greene import greene
from algorithms.takaffoli import takaffoli
from algorithms.louvain_modified import louvain_modified
from algorithms.tiles import tiles
from algorithms.multistep import ms_sum, ms_avg
from helpers import build_sum_graph
from snapshot import Snapshot
import louvain

snapshots = []
communities = []
# create snapshots from graph and extract communities from each one
for i in range(1, 13):
    s = Snapshot(i, "enron2001.txt")
    cs = louvain.find_partition(s.get_graph(), louvain.ModularityVertexPartition)
    snapshots.append(s)
    clusters = []

    for c in cs:
        if len(c) > 1:
            community = s.get_vertices(c)
            clusters.append(community)

    communities.append(clusters)


# add any algorithm execution here
# greene and takaffoli take communities while everything else snapshots

