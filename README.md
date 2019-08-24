# Dynamic Community Detection Algorithms

***

### General

The project uses the `igraph` library for graph calculations, plotting and static community detection algorithms.
Calculations are mainly done on the Enron email data set (usually a yearly partition of it).

### Installation

The project runs on python 3.7 so a Virtual Environment with this python version is recommended. 
* Use `pip` to install the required libraries from the `wheels` folder on Windows.
This is because compilation of `igraph`'s core does not work on Windows
* For linux you can just `pip install -r requirements.txt`.

***

### Algorithms

This section will be updated with all the dcd algorithms that exist in the project.

#### Instant-Optimal (Iterative similarity-based)

* Greene et al. 2010:
    * Generates a list of all dynamic communities over a timeline of static graphs (snapshots).
    * Arguments:
        * `step_communities`: A list containing all the communities of each `snapshot` in chronological order
        (e.g. for 2 snapshots: `[[...snapshot1_communities],[...snapshot2_communities]]`).
        * `similarity` (default: `0.5`): A float in [0,1] defining the threshold for the Jaccard coefficient for community matching.
        * `death` (default: `3`): An integer defining after how many steps a community dies after remaining unobserved.

* Takaffoli et al. 2011:
    * Generates a list of all dynamic communities over a timeline of static graphs (snapshots).
    * Arguments:
        * `step_communities`: A list containing all the communities of each `snapshot` in chronological order.
        * `similarity` (default: `0.5`): A float in [0,1] defining the similarity threshold for community matching.

#### Temporal Trade-off (Partition update by Global optimization / Set of rules)

* Aynaud and Guillaume et al. 2010:
    * Generates a list of partitions over a timeline of static graphs (snapshots), using the partition at step t-1 to seed the partition at step t.
    * Arguments:
        * `snapshots`: A list containing all of the `snapshot` graphs in chronological order.
        * `randomise_constraint` (default: `0.2`): A float in [0,1] indicating the percentage of nodes in partition at step t-1 to be moved to their own community while seeding partition at step t.
        (`0` runs the stable version of the louvain algorithm while `1` runs the standard louvain algorithm)

* Rossetti et al. 2017:
   * Generates a list of dicts, each one containing all the formed communities at the time of observation.
   * Arguments:
      * `stream`: A list of edges in the format of [node1, node2, weight, timestamp], preferably ordered by timestamp.
      * `ttl`: An integer defining after how much time in days an edge is removed from the graph (time to live).
      * `observe_after` (default: `1`): An integer defining the interval in days after which the communities are observed.
      * `network` (default: `None`): An instance of the `Network` class to be used as the starting network.

#### Cross-Time Communities Discovery (Fixed Memberships, fixed properties)

* Aynaud and Guillaume et al. 2011:
    * sum method:
        * Generates a partition of the graph union over a set of snapshots and returns its modularity 
        (reads the sum_graph from a file, so use the `build_sum_graph` helper method to build and save your graph to a pickle).
        * Arguments:
            * `fname`: The name of the pickle file that contains the graph.
            * `weight` (default: `"interaction"`): The edge weight used by `build_sum_graph` to simplify the graph 
    * average method:
        * Finds the average modularity of a set of consecutive snapshots of a graph
        * Arguments:
            * `snapshots`: A list containing all of the `snapshot` graphs in chronological order.
            * `weights` (default: `{}`): A dict containing the index of each snapshot as the key and the weight of the snapshot as the value.
