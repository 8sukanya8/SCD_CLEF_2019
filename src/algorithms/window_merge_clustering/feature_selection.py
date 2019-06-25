import preprocess_NLP_pkg
from math import ceil, log
import numpy as np
import re
import copy
from src.algorithms.threshold_clustering.cluster_graph import *
from statistics import mean, stdev
import nltk
import collections
import json


def paragraph_tokenizer(string = "", remove_URL = True, remove_empty_paragraphs = True):
    if remove_URL:
        string = re.sub("[\s]+\$URL\$", "", string) # remove URLs
    paragraphs = re.compile(r'\n\n|\n[\s]+\n').split(string)
    paragraphs = list(set(paragraphs))
    if len(paragraphs) == 1:
        paragraphs = nltk.sent_tokenize(string)
        paragraphs = group_texts(paragraphs,5)
    else:
        paragraphs = balance_large_paragraphs(paragraphs)
    if remove_empty_paragraphs:
        paragraphs =remove_empty_para(paragraphs)
    return paragraphs


def balance_large_paragraphs(paragraphs):
    para_length = [len(para) for para in paragraphs]
    mean_para_length = mean(para_length)
    sd_para_length = stdev(para_length)
    new_paragraphs = []
    for i in range(0, len(paragraphs)):
        para = paragraphs[i]
        if len(para) > mean_para_length + sd_para_length:
            splits = nltk.sent_tokenize(para)
            splits = group_texts(splits, 5)
            new_paragraphs = new_paragraphs + splits
        else:
            new_paragraphs.append(para)
    return new_paragraphs


def remove_empty_para(para_list):
    """Given a list of paragraphs, returns a list of paragraphs that are not empty or have chars greater than 10 characters
        Keyword arguments:
            text_list -- a list of texts
    """
    return [para for para in para_list if not(re.match("| |\n| \n|\n\n|\n \n",para) and para.__len__()<200) ]


def para_size_greater_than_n(para_list, n = 0):
    """Given a list of texts, prints the number of characters of each paragraph.
        Keyword arguments:
            text_list -- a list of texts
            n -- return paragraphs of size > n characters
    """
    #for para in para_list:
        #print(len(para))
    if n > 0:
        return [para for para in para_list if len(para)>n]


def group_texts(text_list, n):
    """ Given a list of texts, returns a list of items concatenated n at a time.
        Keyword arguments:
            text_list -- a list of texts
            n -- group n items together at a time
    """
    start = 0
    end = 0
    if n > len(text_list):
        return text_list
    groups = []
    for i in range(0, ceil(text_list.__len__()/n)):
        end = start + n
        cat_text = ""
        for j in range(start, end):
            if j < text_list.__len__():
                cat_text = cat_text + text_list[j] + "\n\n"
        groups.append(cat_text)
        start = end
    return groups


def calculate_window_distance(windows, distance_measure):
    """Given windows, for each window selects features (word/ngram) and calculates distance wrt. other windows. Returns a distance matrix
        Keyword arguments:
            windows -- windows

    """
    dist_m = np.zeros((windows.__len__(),windows.__len__()))
    for i in range(0,windows.__len__()):
        w1 = windows[i]
        for j in range(0,windows.__len__()):
            w2 = windows[j]
            if i!=j:
                dist_m[i][j] = get_window_distance(w1,w2, distance_measure)
                #print(i, j, dist_m[i][j])
    return dist_m


def calculate_window_distance_with_selected_words(windows, distance_measure, selected_words):
    """Given windows, for each window selects features (word/ngram) and calculates distance wrt. other windows. Returns a distance matrix
        Keyword arguments:
            windows -- windows

    """
    dist_m = np.zeros((windows.__len__(),windows.__len__()))
    for i in range(0,windows.__len__()):
        w1 = windows[i]
        for j in range(0,windows.__len__()):
            w2 = windows[j]
            if i!=j:
                dist_m[i][j] = get_window_distance_with_selected_words(w1,w2, distance_measure, selected_words)
                #print(i, j, dist_m[i][j])
    return dist_m


def recalculate_window_distance_with_selected_words(windows, distance_measure, selected_words, w1_index, w2_index, dist_m):
    """Given windows, for each window selects features (word/ngram) and calculates distance wrt. other windows. Returns a distance matrix
        Keyword arguments:
            windows -- windows

    """
    low_w = 0
    high_w = 0
    if w1_index < w2_index:
        low_w = w1_index
        high_w = w2_index
    else:
        low_w = w2_index
        high_w = w1_index
    dist_m = np.delete(dist_m, high_w, axis=0) # remove larger col
    dist_m = np.delete(dist_m, high_w, axis=1) # remove larger row
    dist_m = np.delete(dist_m, low_w, axis=0)
    dist_m = np.delete(dist_m, low_w, axis=0)
    rows = dist_m.shape[0]
    cols = dist_m.shape[1]
    if rows == 0 or cols == 0 : #or windows.__len__ >= rows or windows.__len__ >= cols
        print("Error! Wrong size of distance matrix")
        return None
    return dist_m


def get_window_distance(w1,w2, distance_measure):
    """Given two windows, returns the value of the chosen distance_measure function
        Keyword arguments:
           w1 -- the window from which words are selected
           w2 -- window against which selected words from w1 are compared
           distance_measure -- distance function from preprocess_NLP_pkg

    """
    selected_words_freq_dist = preprocess_NLP_pkg.word_freq_count(w1, number_of_terms=20) # select words from window 1
    selected_words = list(selected_words_freq_dist.keys())
    word_freq_w1 = preprocess_NLP_pkg.word_freq_count_normalised(w1)
    selected_word_vector_w1 = list(preprocess_NLP_pkg.select_feature_vector(word_freq_w1, selected_words).values())
    word_freq_w2 = preprocess_NLP_pkg.word_freq_count_normalised(w2)
    selected_word_vector_w2 = list(preprocess_NLP_pkg.select_feature_vector(word_freq_w2, selected_words).values())
    try:
        dist = distance_measure(selected_word_vector_w1, selected_word_vector_w2)
        #print(dist)
        return dist
    except NameError:
        print("The function ", distance_measure, " does not exist! Returning None. Distance Matrix will contain None values.")
        return None


def get_window_distance_with_selected_words(w1,w2, distance_measure, selected_words):
    """Given two windows, returns the value of the chosen distance_measure function from a fixed set of selected words
        Keyword arguments:
           w1 -- the window from which words are selected
           w2 -- window against which selected words from w1 are compared
           distance_measure -- distance function from preprocess_NLP_pkg

    """
    word_freq_w1 = preprocess_NLP_pkg.word_freq_count_normalised(w1)
    selected_word_vector_w1 = list(preprocess_NLP_pkg.select_feature_vector(word_freq_w1, selected_words).values())
    word_freq_w2 = preprocess_NLP_pkg.word_freq_count_normalised(w2)
    selected_word_vector_w2 = list(preprocess_NLP_pkg.select_feature_vector(word_freq_w2, selected_words).values())
    try:
        dist = distance_measure(selected_word_vector_w1, selected_word_vector_w2)
        #print(dist)
        return dist
    except NameError:
        print("The function ", distance_measure, " does not exist! Returning None. Distance Matrix will contain None values.")
        return None



def get_linked_windows(dist_matrix, delta = 1.96):
    """Given a dist_matrix, returns those windows which satisfy (2/4) conditions of being below the row and column thresholds for both windows.
    i.e. dist(w1,w2) will be highlighted if cell value is below any two following thresholds,
    row_threshold(w1), row_threshold(w2), col_threshold(w1), col_threshold(w2)
    Row threshold = mean(row) - delta * sd(row)
    Column threshold = mean(col) - delta* sd(col)
        Keyword arguments:
           dist_matrix: a two dimensional matrix representing the distance between windows.
           delta -- 1.96 for lowest 2.5%, 1.64 for lowest 5%, 1.28 for 10%

        """
    links = []
    for i in range(0, len(dist_matrix)):
        for j in range(0, len(dist_matrix)):
            if i > j:
                w1 = i
                w2 = j
                dist_w1_w2 = dist_matrix[w1,w2]
                dist_w2_w1 = dist_matrix[w2,w1]
                row_w1 = dist_matrix[i,:]
                col_w1 = dist_matrix[:, i]
                row_w2 = dist_matrix[j, :]
                col_w2 = dist_matrix[:, j]
                threshold_w1_row_satisfied =  dist_w1_w2 < (mean(row_w1) - delta * stdev(row_w1)) #(mean(row_w1) + delta * stdev(row_w1)) > dist_w1_w2 > (mean(row_w1) - delta * stdev(row_w1))
                threshold_w2_row_satisfied = dist_w2_w1 < (mean(row_w2) - delta * stdev(row_w2))#(mean(row_w2) + delta * stdev(row_w2)) > dist_w2_w1 > (mean(row_w2) - delta * stdev(row_w2))
                threshold_w1_col_satisfied = dist_w2_w1 < (mean(col_w1) - delta * stdev(col_w1)) #(mean(col_w1) + delta * stdev(col_w1)) > dist_w2_w1 > (mean(col_w1) - delta * stdev(col_w1))
                threshold_w2_col_satisfied = dist_w1_w2 < (mean(col_w2) - delta * stdev(col_w2)) #(mean(col_w2) + delta * stdev(col_w2)) > dist_w1_w2 > (mean(col_w2) - delta * stdev(col_w2))
                hints = sum([threshold_w1_col_satisfied, threshold_w1_row_satisfied,
                             threshold_w2_col_satisfied, threshold_w2_row_satisfied])
                #print(w1, w2, hints, dist_w1_w2, (mean(row_w1) - delta * stdev(row_w1)), dist_w2_w1, (mean(row_w2) - delta * stdev(row_w2)))
                if hints >= 2:
                    links.append((w1,w2,hints, dist_w1_w2, dist_w2_w1))
    return links