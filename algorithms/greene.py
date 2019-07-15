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
            if not d.is_dead():

                for c in step:
                    if helpers.jaccard(d.get_front()[0], c) > similarity:
                        if d.get_front()[1] < i+1:  # update the front
                            d.add_community(c, i+1)
                            d.observed()
                        else:  # create a split community
                            split = DynamicCommunity(c, i+1, d.get_timeline())
                            split.define_split(d_idx, i+1)
                            to_add.append(split)
                            print("split")

                if d.get_front()[1] < i+1 and d.unobserved() > death:  # kill inactive communities
                    d.kill()

        # create dynamic communities for unmatched communities
        for c in step:
            matched = False
            for d in dynamic:
                if not d.is_dead() and helpers.jaccard(d.get_front()[0], c) == 1:
                    matched = True
                    break
            if not matched:
                to_add.append(DynamicCommunity(c, i+1))

        dynamic.extend(to_add)

    return dynamic
