import os
import re
import fnmatch
import json

def load_files_from_dir(dir, pattern = None):
    """Given a directory, load files. If pattern is mentioned, load files with given pattern
        Keyword arguments:
            text -- given text
            delimiter - type of delimiter to be used, default value is '\n\n'
    """
    files_in_path = os.listdir(dir)
    docs_names = []
    if pattern is None:
        docs_names = list(file for file in files_in_path if re.search(".txt", file))
    else:
        try:
            docs_names = fnmatch.filter(os.listdir(dir), pattern)
        except TypeError:
            print("Error! pattern should be a string or bytes like object. Returning None")
            docs_names = None
    return docs_names


def load_txt_to_dict_vk(filepath, delimiter = ','):
    """Given a filepath, load the contents in the format value,key into a dictionary in the format (key:value)
        Keyword arguments:
            filepath -- path to text file
            delimiter - type of delimiter to be used, default value is ','
    """
    d = {}
    with open(filepath) as f:
        for line in f:
            if not line.startswith("#"):
                line = re.sub('\n', '',line)
                (val, key) = line.split(delimiter)
                val_list = []
                if d.get(key):
                    val_list = val_list + d.get(key) + [val]
                    d[key] = val_list
                else:
                    val_list = val_list + [val]
                    d[key] = val_list
    return d


def load_txt_to_dict_kv(filepath, delimiter = ','):
    """Given a filepath, load the contents in the format key,value into a dictionary in the format (key:value)
        Keyword arguments:
            filepath -- path to text file
            delimiter - type of delimiter to be used, default value is ','
    """
    d = {}
    with open(filepath) as f:
        for line in f:
            if not line.startswith("#"):
                line = re.sub('\n', '',line)
                (key, val) = line.split(delimiter)
                d[key] = val
    return d


def convert_dict_values_to_list(d, separator = ' '):
    """Given a filepath, load the contents in the format value,key into a dictionary in the format (key:value)
        Keyword arguments:
            filepath -- path to text file
            delimiter - type of delimiter to be used, default value is ','
    """
    for key in d.keys():
        d[key] = d.get(key).split(separator)
    return d


def write_result_to_output_dir(path, filename, result):
    """ Writes the number of authors to a given file at a given location
    :param path: output directory path
    :param filename: output filename path
    :param result: number of authors
    :return:
    """
    if not os.path.exists(path):
        os.makedirs(path)
    with open(path + filename, 'w') as f:
        json.dump({"authors": result}, f)