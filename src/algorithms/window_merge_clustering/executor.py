
from src.algorithms.window_merge_clustering.feature_selection import calculate_window_distance_with_selected_words
import re
import preprocess_NLP_pkg
from statistics import mean, stdev
from src.algorithms.preprocessing import paragraph_tokenizer
from src.algorithms.window_merge_clustering.ClusterCollection import ClusterCollection
from src.algorithms.window_merge_clustering.Cluster import Cluster
import numpy as np
from src.algorithms.threshold_clustering.executor import is_duplicated


def update_cluster_label(windows, selected_words):
    """
    Calculates distance matrix, finds the windows which have the most similarity, merges the labels of those windows
    and returns the updated cluster labels
    :param windows: list of windows (text)
    :param selected_words: list of selected word features
    :return: updated cluster labels
    """
    labels = ['w'+str(i) for i in range(0,len(windows))]
    cluster_labels = []
    while len(windows)>1:
        result = calculate_window_distance_with_selected_words(windows, preprocess_NLP_pkg.symmetric_kullback_leibler_divergence, selected_words)
        flat = np.array([val for val in result.flatten() if val>0])
        min = flat.min()
        w1, w2 = np.where(result == min)
        #print(labels[w1[0]], labels[w2[0]], min)
        cluster_labels.append((labels[w1[0]], labels[w2[0]], min))
        windows, labels = merge_windows(w1[0],w2[0], windows, labels)
    return cluster_labels


def generate_clusters(cluster_labels):
    """
    Accepts cluster labels in the format [("w0w1", "w3", dist)]. For each label, identifies how many windows are
    present in position 1 and 2.
     -If both positions contain 1 window each, a new cluster is created with these two as members
     -If one position contains 1 window and the other more than one windows, then the case is treated as adding a
    member to a cluster
     -If both positions contain more than one windows, then the case is treated as merging two clusters.
    :param cluster_labels: labels of the clusters. For example, label (w1w2) means a cluster with members window 1
    and window2
    :return: a ClusterCollection object
    """
    cluster_list_obj = ClusterCollection()
    for label in cluster_labels:
        windows_pos_1 = list(set(re.findall('w\d*', label[0])))
        windows_pos_2 = list(set(re.findall('w\d*', label[1])))
        dist = label[2]
        if len(windows_pos_1) ==1 and len(windows_pos_2)>1:
            # treat as adding a member to a cluster
            member = windows_pos_1[0]
            existing_cluster = cluster_list_obj.find_cluster_with_members(windows_pos_2)
            if existing_cluster is not None:
                new_cluster = Cluster(member1=member, distance = dist, cluster1 = existing_cluster)
                cluster_list_obj.add_cluster(new_cluster)
            else:
                print("Error! No cluster found containing members", windows_pos_2, "\n Skipping entry", windows_pos_1, windows_pos_2)

        elif len(windows_pos_2) ==1 and len(windows_pos_1)>1:
            # treat as adding a member to a cluster
            member = windows_pos_2[0]
            existing_cluster = cluster_list_obj.find_cluster_with_members(windows_pos_1)
            if existing_cluster is not None:
                new_cluster = Cluster(member1=member, distance=dist, cluster1=existing_cluster)
                cluster_list_obj.add_cluster(new_cluster)
            else:
                print("Error! No cluster found containing members", windows_pos_2, "\n Skipping entry", windows_pos_2, windows_pos_1)
        elif len(windows_pos_1)==1 and len(windows_pos_2)==1:
            # treat as creating a cluster with two members
            member1 = windows_pos_1[0]
            member2 = windows_pos_2[0]
            new_cluster = Cluster(member1=member1, distance=dist, member2= member2)
            cluster_list_obj.add_cluster(new_cluster)
        elif len(windows_pos_1)>1 and len(windows_pos_2)>1:
            # treat as merging two clusters together
            existing_cluster_1 = cluster_list_obj.find_cluster_with_members(windows_pos_1)
            existing_cluster_2 = cluster_list_obj.find_cluster_with_members(windows_pos_2)
            if existing_cluster_1 is not None and existing_cluster_2 is not None:
                new_cluster = Cluster(distance=dist, cluster1=existing_cluster_1, cluster2 = existing_cluster_2)
                cluster_list_obj.add_cluster(new_cluster)
        #cluster_list_obj.print()
    #cluster_list_obj.print()
    return cluster_list_obj


def merge_windows(w1_index,w2_index, windows, cluster_labels):
    """
    Merges the two given windows and returns updated merged windows and corresponding labels
    :param w1_index: window 1 index
    :param w2_index: window 2 index
    :param windows: list of windows (text)
    :param cluster_labels: labels of the clusters. For example, label (w1w2) means a cluster with members window 1
    and window2
    :return: new merged windows and new labels
    """
    #print(w1,w2,labels)
    new_windows = [val for index,val in enumerate(windows) if index not in [w1_index,w2_index]]
    selected_indices = [i for i in range(0, len(cluster_labels)) if i not in [w1_index, w2_index]]
    new_labels = [cluster_labels[i] for i in selected_indices]
    new_windows.append(windows[w1_index] + windows[w2_index])
    new_labels.append(cluster_labels[w1_index]+cluster_labels[w2_index])
    #print(new_labels)
    return (new_windows, new_labels)


def get_number_of_authors(cluster_list_obj, rejected_windows, windows):
    """
    Uses the length of the cluster_list_obj to generate a preliminary number of authors. Thereafter, the size of the
    rejected windows which could not be part of any cluster are evaluated. If char count of the rejected windows are
    found to be of significant length, then the number of authors is increased.
    :param cluster_list_obj:
    :param rejected_windows:
    :param windows:
    :return:
    """
    # increases author number for each rejected windows size > mean windows size
    #print("rejected", rejected_windows)
    authors = len(cluster_list_obj)
    if rejected_windows is None:
        return authors
    labels = ['w' + str(i) for i in range(0, len(windows))]
    win_len_arr = np.array([len(win) for win in windows])
    greater_than_threshold = 0
    for i in range(0, len(windows)):
        if labels[i] in rejected_windows:
            #print(labels[i], len(windows[i]), mean(win_len_arr),stdev(win_len_arr))
            if len(windows[i]) > (mean(win_len_arr) +stdev(win_len_arr)):
                #print("Author num bumped")
                greater_than_threshold = greater_than_threshold +1
    authors = authors + greater_than_threshold
    return authors


def execute_window_merge_clustering(text, use_duplication_feature= True):
    """
    From a text, creates a distance matrix from windows. Iteratively, most similar windows are merged and
    distance matrix recalculated. Iteration stops when there are no more windows to merge.
    :param text: text for which clustering is to be determined
    :param use_duplication_feature: Boolean for whether to use duplication for prediction
    :return: number of authors
    """
    try:
        if use_duplication_feature:
            if is_duplicated(text) < 2:
                number_of_authors = 1
                return number_of_authors
        windows = paragraph_tokenizer(text, remove_url=True, remove_empty_paragraphs=True)
        selected_words_freq_dist = preprocess_NLP_pkg.word_freq_count(text, number_of_terms=50)
        selected_words = list(selected_words_freq_dist.keys())
        new_cluster_labels = update_cluster_label(windows, selected_words)
        cluster_list_obj = generate_clusters(new_cluster_labels)
        trimmed_cluster_list_obj, rejected_windows = cluster_list_obj.cut_clusters_with_threshold(threshold=0.5)
        number_of_authors = get_number_of_authors(trimmed_cluster_list_obj, rejected_windows, windows)  # len(cluster_list_obj_cut)#
        if number_of_authors == 0:
            number_of_authors = 1
    except:
        print("Something went wrong. Appending the predicted authors with a 1")
        number_of_authors = 1
    return number_of_authors