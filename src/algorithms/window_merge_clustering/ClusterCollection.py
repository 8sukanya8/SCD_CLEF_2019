
class ClusterCollection:
    """
    This class creates and manages a list of clusters
    """
    clusters =[]

    def __init__(self):
        """
        Intiates an empty ClusterCollection
        """
        self.clusters = []

    def find_cluster_with_members(self, members):
        """
        Find the largest cluster which have the given members
        :param members: the members to find
        :return: a cluster
        """
        max_size = 0
        max_cluster = None
        for c in self.clusters:
            all_present = True
            for m in members:
                if not c.member_is_present(m):
                    all_present = False
            if all_present:
                if max_size < c.distance:
                    max_size = c.distance
                    max_cluster = c
        return max_cluster

    def find_biggest_cluster_with_member(self, member):
        """
        Finds the biggest cluster(distance wise) which contains the given member
        :param member: name of a node
        :return: a cluster
        """
        max_size = 0
        max_cluster = None
        for c in self.clusters:
            if c.member_is_present(member):
                if max_size < c.distance:
                    max_size = c.distance
                    max_cluster = c
        return max_cluster

    def add_cluster(self, cluster):
        """
        Append a cluster to the cluster list
        :param cluster:
        :return: None
        """
        if cluster not in self.clusters:
            self.clusters.append(cluster)

    def cut_clusters_with_threshold(self, threshold = 0.3):
        """
        Cut the dendogram cluster with a given threshold
        :param threshold: fraction of the largest (distance wise) cluster. For example, 0.3 indicates that select
        largest clusters with height < 0.3 * distance of largest cluster
        :return: a tuple of (a set of selected clusters which satisfy the threshold,
        a set of rejected clusters which have distance greater than the threshold)
        """
        # cut the dendogram with threshold
        cluster_dist_list = [c.distance for c in self.clusters]
        if len(cluster_dist_list)>1:
            max_limit = threshold * max(cluster_dist_list)
            cut_clusters = [c for c in self.clusters if c.distance <= max_limit]
            rejected_cluster_member_list = [list(c.members.keys()) for c in self.clusters if c.distance > max_limit]
            rejected_members_flattened = [item for sublist in rejected_cluster_member_list for item in sublist]
            selected_clusters = []
            for c1 in cut_clusters:
                set_c1_members = set(c1.members.keys())
                add_c1 = True
                for c2 in cut_clusters:
                    if c1 != c2:
                        set_c2_members = set(c2.members.keys())
                        if set_c1_members.issubset(set_c2_members):
                            add_c1 = False
                if add_c1:
                    selected_clusters.append(c1)
            selected_cluster_member_list = [list(c.members.keys()) for c in selected_clusters]
            selected_members_flattened = [item for sublist in selected_cluster_member_list for item in sublist]
            selected_members_set = set(selected_members_flattened)
            rejected_members_set = set(rejected_members_flattened).difference(selected_members_set)
            return (selected_clusters, rejected_members_set)
        else:
            return self.clusters,None
    '''
    def select_unique_largest_clusters(self):
        """
        
        :return: 
        """
        tuple_list = [(list(c.members), len(c.members)) for c in self.clusters]
    '''
    def print(self):
        for c in self.clusters:
            print(c.members,"\t", c.distance)

