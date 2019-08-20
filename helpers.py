from igraph import Graph


def jaccard(comm1, comm2):
    intersection = len(list(set(comm1).intersection(comm2)))
    union = (len(comm1) + len(comm2)) - intersection

    return float(intersection / union) if union != 0 else -1


def community_sim(comm1, comm2, k):
    intersection = len(list(set(comm1).intersection(comm2)))
    max_size = len(list(set(comm1))) if len(list(set(comm1))) > len(list(set(comm2))) else len(list(set(comm2)))

    return 0 if max_size == 0 or float(intersection / max_size) < k else float(intersection / max_size)


def find_dynamic_index(community, step, dynamic_communities=[]):
    for idx, d in enumerate(dynamic_communities):
        if jaccard(community, d.get_timeline[step]) == 1:
            return idx
    return -1


def intersect_many(lists):
    if len(lists) <= 1:
        return set(*lists)

    result = set(lists[0])
    for item in lists[1:]:
        result.intersection(item)
    return result


# builds the a sum_graph from given snapshots and saves it to a pickle file
def build_sum_graph(snapshots, weight="interaction", fname="sumGraph.pkl", combine_edges=True):
    sum_graph = Graph()
    for idx, snapshot in enumerate(snapshots):
        if idx == 0:
            sum_graph = snapshot.get_graph().copy()
            sum_graph.es()[weight] = sum_graph.es()[weight]
            continue
        sum_graph.add_vertices(list(set(snapshot.get_graph().vs()["name"]).difference(set(sum_graph.vs()["name"]))))
        sum_graph.add_edges([
            (snapshot.get_graph().vs.find(e.tuple[0])["name"],
             snapshot.get_graph().vs.find(e.tuple[1])["name"])
            for e in snapshot.get_graph().es()
        ])

        sum_graph.es(lambda e: e[weight] is None)[weight] = snapshot.get_graph().es()[weight]

    if combine_edges:
        sum_graph.simplify(combine_edges={weight: sum})
    sum_graph.write_pickle(fname=fname)
