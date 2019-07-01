from dynamic_community import DynamicCommunity
from igraph import *
import helpers

'''Dynamic Community Detection algorithm based on Takaffoli et al 2011'''


def takaffoli(step_communities, similarity=0.5):
    dynamic = []

    for t, step in enumerate(step_communities):
        # save index in step and index of dc for faster search
        step_communities[t] = [{"community": community, "idx": idx, "dc": -1} for idx, community in enumerate(step)]

        if t == 0:
            pass
            for idx in range(len(step)):
                dynamic.append(DynamicCommunity(step_communities[t][idx]["community"]))
                step_communities[t][idx]["dc"] = len(dynamic) - 1
        else:
            remaining_in_step = step_communities[t].copy()

            # go backwards until every community is matched
            for prev_step in range(t - 1, -1, -1):
                bipartite = {"vs": [], "es": [], "ws": []}
                not_matched = []

                for c_idx, community in enumerate(remaining_in_step):
                    matched = False
                    # match communities with previous steps
                    for p_idx, prev in enumerate(step_communities[prev_step]):
                        weight = helpers.community_sim(community["community"], prev["community"], similarity)
                        if weight > 0:
                            matched = True
                            bipartite["vs"].extend(["p"+str(p_idx), "c"+str(c_idx)])
                            bipartite["es"].append(("p"+str(p_idx), "c"+str(c_idx)))
                            bipartite["ws"].append(weight)

                    if not matched:
                        not_matched.append(community)

                # construct the bipartite graph
                b = Graph()
                b.add_vertices(list(set(bipartite["vs"])))
                b.vs["type"] = [vertex[0] == "p" for vertex in b.vs["name"]]
                b.add_edges(bipartite["es"])
                b.es["weight"] = bipartite["ws"]
                b_matching = b.maximum_bipartite_matching("type", "weight").matching

                # match communities to their dynamic communities according to the maximum bipartite matching
                for i, j in enumerate(b_matching):
                    if b.vs[i]["name"][0] == "p":
                        # interested in current step (name starts with 'c')
                        pass
                    elif j == -1:
                        # -1 means community is unmatched to any previous communities
                        c_idx = int(b.vs[i]["name"][1:])
                        community = remaining_in_step[c_idx]
                        not_matched.append(community)
                    else:
                        prev_idx = int(b.vs[j]["name"][1:])
                        prev_comm = step_communities[prev_step][prev_idx]
                        # check if front is current step and split before adding
                        c_idx = int(b.vs[i]["name"][1:])
                        dynamic[prev_comm["dc"]].add_community(remaining_in_step[c_idx]["community"], t)
                        print(dynamic[prev_comm["dc"]].get_timeline())
                        return

                # if no previous steps remain create dynamic communities for each unmatched community
                if prev_step == 0:
                    for community in not_matched:
                        d = DynamicCommunity(community["community"], t)
                        dynamic.append(d)
                        step_communities[t][community["idx"]]["dc"] = len(dynamic) - 1

                # set not matched communities as the remaining
                elif len(not_matched) != 0:
                    remaining_in_step = not_matched.copy()
                else:
                    break
