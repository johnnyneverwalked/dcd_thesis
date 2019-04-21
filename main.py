from igraph import *
from snapshot import Snapshot
from greene import greene


snapshots = []
communities = []

# create snapshots from graph and extract communities from each one
for i in range(1, 13):
    s = Snapshot(i, "enron2001.txt")
    cs = s.get_graph().community_infomap()
    snapshots.append(s)
    clusters = []

    for c in cs:
        community = s.get_vertices(c)

        if len(community) > 1:
            clusters.append(community)

    communities.append(clusters)


dynamicSet = greene(communities)


for d in dynamicSet:
    if not d.is_dead():
        print(d.get_timeline())
