from dynamic_community import DynamicCommunity
import helpers

'''Dynamic Community detection algorithm based on Greene et al 2010'''


def greene(step_communities, similarity=0.5, death=3):
    dynamic = []

    for community in step_communities[0]:
        dynamic.append(DynamicCommunity(community))

    del step_communities[0]

    for i, step in enumerate(step_communities):
        to_add = []

        # match communities to fronts
        for d_idx, d in enumerate(dynamic):
            if d.is_dead() is None:

                for c in step:
                    if helpers.jaccard(dynamic[d_idx].get_front()[0], c) > similarity:
                        if dynamic[d_idx].get_front()[1] < i+1:  # update the front
                            dynamic[d_idx].add_community(c, i+1)
                        else:  # create a split community
                            split = DynamicCommunity(c, i+1, dynamic[d_idx].get_timeline())
                            split.define_split(d_idx, i+1)
                            to_add.append(split)
                        dynamic[d_idx].observed()

                # kill inactive communities
                if dynamic[d_idx].get_front()[1] < i+1 and dynamic[d_idx].unobserved() > death:
                    dynamic[d_idx].kill(i+1)

        # create dynamic communities for unmatched communities
        for c in step:
            matched = False
            for d in dynamic:
                if d.is_dead() is None and helpers.jaccard(d.get_front()[0], c) == 1:
                    matched = True
                    break
            if not matched:
                to_add.append(DynamicCommunity(c, i+1))

        dynamic.extend(to_add)

    return dynamic
