# Dynamic Community Detection Algorithms

***

### General

The project uses the `igraph` library for graph calculations, plotting and static community detection algorithms (mainly infomap).
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
        (e.g. for 2 snapshots: `[[...snapshot1_communities],[...snapshot2_communities]]`)
        * `similarity` (default: `0.5`): A float in [0,1] defining the threshold for the Jaccard coefficient for community matching.
        * `death` (default: `3`): An integer defining after how many steps a community dies after remaining unobserved.

* Takaffoli et al. 2011:
    * Generates a list of all dynamic communities over a timeline of static graphs (snapshots).
    * Arguments:
        * `step_communities`: A list containing all the communities of each `snapshot` in chronological order
        * `similarity` (default: `0.5`): A float in [0,1] defining the threshold for the similarity threshold for community matching.

#### Temporal Trade-off (Partition update by Global optimization, Informed  CD  by Network Smoothing)
