from igraph import *
from datetime import datetime
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
        return node["core_in_communities"].copy().extend(node["peripheral_in_communities"].copy())

    def create_community(self, nodes):
        self._communities[self._cid] = nodes
        for node in nodes:
            node["core_in_communities"].append(self._cid)
        self._cid += 1
        return self._cid

    def update_node_roles(self, community_id, node_ids):
        if community_id not in self._communities.keys():
            return

        nodes = self._graph.vs(node_ids)
        for v in nodes:
            central = False
            v_neighbors = self._graph.vs(v.neighbors())
            for n1 in v_neighbors:
                if community_id not in n1["core_in_communities"]:
                    continue
                if central:
                    break
                for n2 in self._graph.vs(n1.neighbors()):
                    if n2.index == v.index or community_id not in n1["core_in_communities"]:
                        continue
                    if (len(self._graph.es((v.index, n1.index))) and
                            len(self._graph.es((v.index, n2.index))) and
                            len(self._graph.es((n1.index, n2.index)))):
                        central = True
                        break
            if central:
                if community_id not in v["core_in_communities"]:
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
        if not self._graph.vs(name=name).indices:
            self._graph.add_vertex(name,
                                   core_in_communities=[],
                                   peripheral_in_communities=[])
        return self._graph.vs.find(name)

    def add_edge(self, triplet):
        edges = self._graph.es((triplet[0], triplet[1]))
        if not edges.indices:
            self._graph.add_edge(triplet[0],
                                 triplet[1],
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
        u_neighbors = self._graph.vs(u.neighbors())
        v_comm = self.get_node_communities(v)
        v_neighbors = self._graph.vs(v.neighbors())

        for z in self._graph.vs(list(set(u.neighbors()).intersection(v.neighbors()))):
            z_comm = z["core_in_communities"].copy().extend(z["peripheral_in_communities"].copy())
            z_neighbors = self._graph.vs(z.neighbors())

            if len(intersect_many([u_comm, v_comm, z_comm])):
                self.create_community([u, v, z])
                self.peripheral_propagation(u, u_neighbors)
                self.peripheral_propagation(v, v_neighbors)
                self.peripheral_propagation(z, z_neighbors)

            elif len(intersect_many([u_comm, v_comm])):
                self.add_to_core(z, list(intersect_many([u_comm, v_comm])))
                self.peripheral_propagation(z, z_neighbors)

            elif len(intersect_many([u_comm, z_comm])):
                self.add_to_core(v, list(intersect_many([u_comm, z_comm])))
                self.peripheral_propagation(v, v_neighbors)

            elif len(intersect_many([v_comm, z_comm])):
                self.add_to_core(u, list(intersect_many([v_comm, z_comm])))
                self.peripheral_propagation(u, u_neighbors)

    def add_to_core(self, node, core_communities):
        for c in core_communities:
            if c not in node["core_in_communities"]:
                node["core_in_communities"].append(c)
                self._communities[c].append(node)
            if c in node["peripheral_in_communities"]:
                node["peripheral_in_communities"].remove(c)


def tiles(stream, ttl, observe_after=1, network=None):
    if network is None:
        network = Network()
    remove_queue = []
    communities = dict()
    actual_t = None

    for connection in stream:
        timestep = datetime.fromtimestamp(connection[3])
        if actual_t is None:
            actual_t = timestep
        # (u,v,t)
        triplet = (connection[0], connection[1], int(connection[3]))
        remove_queue.append(triplet)
        remove_expired(network, remove_queue, ttl, timestep)

        source = network.add_vertex(triplet[0])
        target = network.add_vertex(triplet[1])
        network.add_edge(triplet)

        source_n = source.neighbors()
        target_n = target.neighbors()

        if len(source_n) == 1 and len(target_n) == 1:
            continue
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
    for triplet in queue:
        time_added = datetime.fromtimestamp(triplet[2])

        if (current - time_added).days >= ttl:
            source = network.get_graph().vs.find(name=triplet[0])
            target = network.get_graph().vs.find(name=triplet[1])

            network.get_graph().delete_edges((source.index, target.index))

            to_update = network.get_graph().vs(list(set(source.neighbors())
                                                    .intersection(target.neighbors())
                                                    .union([source.index, target.index])))

            communities = intersect_many([network.get_node_communities(source), network.get_node_communities(target)])
            for community in communities:

                components = network.get_graph().subgraph(network.get_community_nodes(community).indices).clusters
                if len(components) == 1:
                    network.update_node_roles(community, to_update)
                else:
                    for c in components:
                        cid = network.create_community(c)
                        network.remove_community_nodes(community, c)
                        network.update_node_roles(cid, c)
        else:
            break
