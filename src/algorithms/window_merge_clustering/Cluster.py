import copy


class Cluster:
    members = {}
    distance = 0
    def __init__(self, member1=None, distance =0, member2=None, cluster1 = None, cluster2 = None): # at first cluster distance should be zero or maximum?
        """Initialises a cluster in three possible ways
        (1) Only two members:
            Args: member1 - name of member1, member2 - name of member2, distance = some distance , cluster1= None, cluster2 = None
        (2) Add member1 to a cluster
            Args: member1 - name of member1, member2 - None, distance = some distance , cluster1= some cluster, cluster2 = None
        (3) Merge two clusters
            Args: member1 - None, member2 - None since no extra member is involved, distance = some distance between clusters , cluster1= some cluster, cluster2 = some cluster
                Keyword arguments:
                    member1 -- a new member to be added
                    member2 -- a new member to be added
                    distance - represents the distance from a new member or the distance between two clusters. Exercise caution.
                    cluster1 -- a cluster
                    cluster2 -- a cluster
        """
        self.members = {}
        self.distance = 0
        if cluster1 is None and cluster2 is None:
            if member1 is None or member2 is None:
                print("Error! Not sufficient information provided to create a cluster")
            elif member1 in self.members.keys() or member2 in self.members.keys():
                print("Error! Attempting to re-add a member to a cluster")
            else:
                self.members[member1] = 0
                self.members[member2] = distance
                self.distance = distance
        elif cluster2 is None and cluster1 is not None:
            if member2 is not None:
                print("Error! When member 1 is being added, member 2 should be None")
            else:
                if member1 is None or member1 in self.members.keys():
                    print("Error! Attempting to add a None member or re-add a member to a cluster") # cluster2.members.keys()
                else:
                    self.members = copy.deepcopy(cluster1.members)
                    self.members[member1] = distance
                    self.distance = copy.deepcopy(cluster1.distance) + distance
        elif cluster1 is None and cluster2 is not None:
            print("Error! Cluster1 cannot be none when Cluster2 is not None!") # avoid condition
        else:
            cluster1_members = copy.deepcopy(cluster1.members)
            cluster2_members = copy.deepcopy(cluster2.members)
            self.members = {**cluster1_members, **cluster2_members} # add two dictionaries
            self.distance = max(copy.deepcopy(cluster1.distance), copy.deepcopy(cluster2.distance)) + distance

    def member_is_present(self, member):
        return member in self.members

'''
c = Cluster(member1 = 'w0',distance = 0.42, member2='w6')
c_list = ClusterCollection(c)
c_list.add_cluster(Cluster(member1='w5', distance = 0.47166036112, member2=None, cluster1 = c, cluster2 = None))
new_c = copy.deepcopy(c_list.find_biggest_cluster_with_member('w0'))
c_list.add_cluster(Cluster(member1='w4', distance = 0.45513326279, member2=None, cluster1 = new_c, cluster2 = None))
new_c = copy.deepcopy(c_list.find_biggest_cluster_with_member('w0'))
c_list.add_cluster(Cluster(member1='w8', distance = 0.45374750711, member2=None, cluster1 = new_c, cluster2 = None))
new_c = copy.deepcopy(c_list.find_biggest_cluster_with_member('w0'))
c_list.add_cluster(Cluster(member1='w3', distance = 0.47163155187, member2=None, cluster1 = new_c, cluster2 = None))
new_c = copy.deepcopy(c_list.find_biggest_cluster_with_member('w0'))
c_list.add_cluster(Cluster(member1='w7', distance = 0.495231566163, member2=None, cluster1 = new_c, cluster2 = None))

c = Cluster(member1 = 'w9',distance = 0.51041739833, member2='w12')
c_list.add_cluster(c)
new_c = copy.deepcopy(c_list.find_biggest_cluster_with_member('w0'))
c_list.add_cluster(Cluster(member1=None, distance = 0.482114558353, member2=None, cluster1 = new_c, cluster2 = c))
new_c = copy.deepcopy(c_list.find_biggest_cluster_with_member('w0'))
c_list.add_cluster(Cluster(member1='w1', distance =0.519188247165, member2=None, cluster1 = new_c, cluster2 = None))
new_c = copy.deepcopy(c_list.find_biggest_cluster_with_member('w0'))
c_list.add_cluster(Cluster(member1='w2', distance =0.502902930385, member2=None, cluster1 = new_c, cluster2 = None))
new_c = copy.deepcopy(c_list.find_biggest_cluster_with_member('w0'))
c_list.add_cluster(Cluster(member1='w11', distance =0.587370062122, member2=None, cluster1 = new_c, cluster2 = None))
new_c = copy.deepcopy(c_list.find_biggest_cluster_with_member('w0'))
c_list.add_cluster(Cluster(member1='w10', distance =0.604362050946, member2=None, cluster1 = new_c, cluster2 = None))

'''
