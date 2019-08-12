from igraph import *
from datetime import datetime
from time import time
from helpers import intersect_many


class Network:
    def __init__(self, graph=None, communities=None):
        if graph is not None:
            self._graph = graph
        else:
            self._graph = Graph()

        if communities is not None:
            self._communities = communities
            self._cid = len(communities)
        else:
            self._communities = dict()
            self._cid = 0
            self.r = 0

    def get_graph(self):
        return self._graph

    def get_communities(self):
        current_communities = dict()
        for c in self._communities.keys():
            current_communities[c] = self.get_community_nodes(c)["name"]
        return current_communities

    def get_community_nodes(self, community_id):
        return self._graph.vs(lambda v:
                              community_id in v["core_in_communities"] or
                              community_id in v["peripheral_in_communities"])

    def get_node_communities(self, node):
        comms = node["core_in_communities"].copy()
        comms.extend(node["peripheral_in_communities"].copy())
        return comms

    def create_community(self, nodes):
        self._communities[self._cid] = nodes
        for node in nodes:
            node["core_in_communities"].append(self._cid)
        self._cid += 1
        return self._cid

    def update_node_roles(self, community_id, nodes):
        if community_id not in self._communities.keys():
            return

        for v in nodes:
            central = False
            v_neighbors = v.neighbors()
            v_n_indexes = self._graph.neighbors(v.index)
            for n1 in v_neighbors:
                if central:
                    break
                if community_id not in n1["core_in_communities"]:
                    continue

                n1_neighbors = self._graph.neighbors(n1.index)
                common_n = list(intersect_many([v_n_indexes, n1_neighbors]))

                if common_n:
                    for n2 in self._graph.vs(common_n):
                        if community_id not in n2["core_in_communities"]:
                            continue
                        central = True
                        break

            if central and community_id not in v["core_in_communities"]:
                v["core_in_communities"].append(community_id)
                if community_id in v["peripheral_in_communities"]:
                    v["peripheral_in_communities"].remove(community_id)
                self._communities[community_id].append(v)
            else:
                self.remove_community_nodes(community_id, [v])
                v["peripheral_in_communities"].append(community_id)
                for n in v_neighbors:
                    if community_id in n["peripheral_in_communities"]:
                        n["peripheral_in_communities"].remove(community_id)

    def remove_community_nodes(self, community_id, node_ids):
        if community_id not in self._communities.keys():
            return

        self._communities[community_id] = list(filter(
            lambda node: node.index not in node_ids,
            self._communities[community_id]
        ))

        for node in list(filter(lambda v: v.index in node_ids, self.get_community_nodes(community_id))):
            if community_id in node["core_in_communities"]:
                node["core_in_communities"].remove(community_id)
            if community_id in node["peripheral_in_communities"]:
                node["peripheral_in_communities"].remove(community_id)

    def add_vertex(self, name):
        if not (len(self._graph.vs) and self._graph.vs(name=name).indices):
            self._graph.add_vertex(name,
                                   core_in_communities=[],
                                   peripheral_in_communities=[])
        return self._graph.vs.find(name)

    def add_edge(self, triplet):
        edges = self._graph.es(_source=triplet[0].index, _target=triplet[1].index)
        if not edges.indices:
            self._graph.add_edge(triplet[0].index,
                                 triplet[1].index,
                                 timestamp=triplet[2])
        else:
            edges["timestamp"] = triplet[2]

    def peripheral_propagation(self, u, nodes):
        for v in nodes:
            for comm in u["core_in_communities"]:
                if comm not in v["core_in_communities"] and comm not in v["peripheral_in_communities"]:
                    v["peripheral_in_communities"].append(comm)

    def core_propagation(self, u, v):
        u_comm = self.get_node_communities(u)
        u_neighbors = u.neighbors()
        v_comm = self.get_node_communities(v)
        v_neighbors = v.neighbors()

        for z in self._graph.vs(list(set(u.neighbors()).intersection(v.neighbors()))):
            z_comm = self.get_node_communities(z)
            z_neighbors = z.neighbors()

            if intersect_many([u_comm, v_comm, z_comm]):
                self.create_community([u, v, z])
                self.peripheral_propagation(u, u_neighbors)
                self.peripheral_propagation(v, v_neighbors)
                self.peripheral_propagation(z, z_neighbors)

            elif intersect_many([u_comm, v_comm]):
                self.add_to_core(z, list(intersect_many([u_comm, v_comm])))
                self.peripheral_propagation(z, z_neighbors)

            elif intersect_many([u_comm, z_comm]):
                self.add_to_core(v, list(intersect_many([u_comm, z_comm])))
                self.peripheral_propagation(v, v_neighbors)

            elif intersect_many([v_comm, z_comm]):
                self.add_to_core(u, list(intersect_many([v_comm, z_comm])))
                self.peripheral_propagation(u, u_neighbors)

    def add_to_core(self, node, core_communities):
        for c in core_communities:
            if c not in node["core_in_communities"]:
                node["core_in_communities"].append(c)
                self._communities[c].append(node)
            if c in node["peripheral_in_communities"]:
                node["peripheral_in_communities"].remove(c)

    def assert_core(self, u, v, common_neighbors):
        if u["core_in_communities"] or v["core_in_communities"] or not common_neighbors:
            return
        for z in self._graph.vs(common_neighbors):
            if z["core_in_communities"]:
                self.add_to_core(u, z["core_in_communities"])
                self.add_to_core(v, z["core_in_communities"])
            else:
                self.create_community([u, v, z])

            self.peripheral_propagation(u, u.neighbors())
            self.peripheral_propagation(v, v.neighbors())
            self.peripheral_propagation(z, z.neighbors())


def tiles(stream, ttl, observe_after=1, network=None):
    if network is None:
        network = Network()
    stream.sort(key=lambda l: int(l[3]))
    remove_queue = []
    communities = dict()
    actual_t = None
    last_day = None

    for i, connection in enumerate(stream):
        # print(str(format((i*100)/len(stream), ".2f")) + "%")
        if connection[0] == connection[1]:
            # prevent loops
            continue

        timestep = datetime.fromtimestamp(int(connection[3]))

        if actual_t is None:
            actual_t = timestep

        if last_day and (timestep - last_day).days == 0:
            zerodays = True
        else:
            zerodays = False
            last_day = timestep

        # (u,v,t)
        triplet = (connection[0], connection[1], int(connection[3]))
        remove_queue.append(triplet)
        if not zerodays:
            remove_expired(network, remove_queue, ttl, timestep)
        source = network.add_vertex(triplet[0])
        target = network.add_vertex(triplet[1])
        network.add_edge((source, target, timestep))

        source_n = network.get_graph().neighbors(source.index)
        target_n = network.get_graph().neighbors(target.index)

        if len(source_n) == 1 and len(target_n) == 1:
            continue

        common_n = list(set(source_n).intersection(target_n))
        network.assert_core(source, target, common_n)

        if not (len(source["core_in_communities"]) and len(target["core_in_communities"])):
            continue

        if len(source_n) == 1 and len(target_n) > 1:
            network.peripheral_propagation(source, [target])

        elif len(source_n) > 1 and len(target_n) == 1:
            network.peripheral_propagation(target, [source])

        elif not len(set(source_n).intersection(target_n)):
            network.peripheral_propagation(source, [target])
            network.peripheral_propagation(target, [source])

        else:
            network.core_propagation(source, target)

        if (timestep - actual_t).days >= observe_after:
            communities[len(communities)] = network.get_communities()
            actual_t = timestep

    communities[len(communities)] = network.get_communities()
    return communities


def remove_expired(network, queue, ttl, current):
    q = queue.copy()
    for triplet in q:
        time_added = datetime.fromtimestamp(triplet[2])

        if (current - time_added).days >= ttl:
            source = network.get_graph().vs.find(name=triplet[0])
            target = network.get_graph().vs.find(name=triplet[1])

            if network.get_graph().es(_source=source.index, _target=target.index).indices:
                continue
            network.get_graph().delete_edges([(source.index, target.index)], timestamp=triplet[2])

            common = set(network.get_graph().neighbors(source.index)).intersection(
                network.get_graph().neighbors(target.index)).union([source.index, target.index])
            to_update = network.get_graph().vs(list(common))

            communities = list(intersect_many([
                network.get_node_communities(source),
                network.get_node_communities(target)
            ]))

            for community in communities:

                components = network.get_graph().subgraph(network.get_community_nodes(community).indices).clusters()
                if len(components) == 1:
                    start = time()
                    network.update_node_roles(community, to_update)
                    # print("update in:", round((time() - start) * 1000))
                else:
                    start = time()
                    for c in components:
                        nodes = network.get_graph().vs(c)
                        cid = network.create_community(nodes)
                        network.remove_community_nodes(community, nodes)
                        network.update_node_roles(cid, nodes)
                    print("split in:", round((time() - start) * 1000))
            queue.pop(0)
        else:
            break
