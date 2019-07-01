
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
