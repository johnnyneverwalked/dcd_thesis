from algorithms.takaffoli import takaffoli
from algorithms.greene import greene
from algorithms.louvain_modified import louvain_modified
from algorithms.tiles import tiles
from snapshot import Snapshot
from igraph import *
import datetime


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

# Greene execution

greeneSet = greene(communities)

for d in greeneSet:
    if not d.is_dead():
        print(d.get_timeline())

print(len(greeneSet))
print("----GREENE COMMUNITIES----")

# Takaffoli execution

takaffoliSet = takaffoli(communities)

for d in takaffoliSet:

    print(d.get_timeline())
print(len(takaffoliSet))
print("----TAKAFFOLI COMMUNITIES----")

# Aynaud-Guillaume execution

louvainSet = louvain_modified(snapshots, randomise_constraint=0.02)
for p in louvainSet:
    print(p.summary())
print("----LOUVAIN-MOD COMMUNITIES----")

# TILES execution

stream = []
with open('enron2001.txt', 'r') as enron:
    for line in enron:
        tokens = line.split(" ")
        stream.append(tokens)

tilesSet = tiles(stream, 2)
for tile in tilesSet.values():
    print(len(tile), tile)
print("----TILES COMMUNITIES---")

# teeeest
# g = Graph()
# g.add_vertices(["1", "2", "3", "4"])
# g.vs["list"] = [[1, 2], [3, 4], [5, 6], [7, 8]]
# g.add_edges([("1", "2"), ("3", "4")])
# s = g.subgraph([0, 1])
# print(g.subgraph([0, 1]).clusters()[0])
