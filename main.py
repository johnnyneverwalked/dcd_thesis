from snapshot import Snapshot
from greene import greene
from takaffoli import takaffoli

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

# greene execution

greeneSet = greene(communities)

for d in greeneSet:
    if not d.is_dead():
        print(d.get_timeline())

print(len(greeneSet))
print("----GREENE COMMUNITIES----")

# takaffoli execution

takaffoliSet = takaffoli(communities)
for d in takaffoliSet:
    print(d.get_timeline())
print(len(takaffoliSet))
print("----TAKAFFOLI COMMUNITIES----")
