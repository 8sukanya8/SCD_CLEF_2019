#!/usr/bin/env python
"""main.py: Applies the TBC and WMC algorithms on the files of the input folder to predict
the number of authors."""
__author__  = "Sukanya Nath"
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Sukanya Nath"

import preprocess_NLP_pkg
from src.algorithms.window_merge_clustering.executor import execute_window_merge_clustering
from src.algorithms.threshold_clustering.executor import execute_threshold_clustering
from src.load_data import write_result_to_output_dir
import re
import sys
import getopt


if __name__ == '__main__':
    inputFolder = ""
    outputFolder = ""
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:o:")
    except getopt.GetoptError:
        print("main.py -i <inFolder> -o <outFolder>")  # tira command format
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-i":
            inputFolder = arg
        elif opt == "-o":
            outputFolder = arg
    assert len(inputFolder) > 0      # if not true, stop the process
    print("Input folder is", inputFolder)
    assert len(outputFolder) > 0
    print ("Output folder is", outputFolder)
    files = preprocess_NLP_pkg.load_files_from_dir(inputFolder, '*.txt')
    files.sort()
    for i in range(0, len(files)):
        file = files[i]
        training_text = preprocess_NLP_pkg.read_file(inputFolder + "/" + file, mode='rb',
                                                         ignore_comments=False).decode('utf-8')
        prediction_TBC = execute_threshold_clustering(training_text, merge_threshold=50, add_node_threshold=50,
                                                    prune=True, number_of_terms=50,
                                                    distance_measure=preprocess_NLP_pkg.manhattan_distance,
                                                    use_duplication_feature= True)
        prediction_WMC = execute_window_merge_clustering(training_text, use_duplication_feature= True)
        print("file: ", file, " TBC: ", prediction_TBC, " WMC: ", prediction_WMC)
        output_file_mod_TBC = output_file_mod_WMC = re.sub(".txt", ".truth", file)
        write_result_to_output_dir(path=outputFolder + "/TBC/", filename=output_file_mod_TBC, result=prediction_TBC)
        write_result_to_output_dir(path=outputFolder + "/WMC/", filename=output_file_mod_WMC, result=prediction_WMC)


