
from PythonScripts.Utils.Travis_Utils import get_travis_repo
import pandas as pd
import os
import sys
import time

import multiprocessing as mp
df_nonml=pd.read_csv('../../CSV Input - New/NonML-classification.csv',sep=';')
# df_tool=pd.read_csv('../../CSV Inputs/ToolProjects_classification.csv')

# l_applied_plus=['AliOsm/arabic-text-diacritization', 'BjornFJohansson/pydna', 'LindseyB/not-pepe', 'PaddlePaddle/LARK', 'PaddlePaddle/VisualDL', 'SINTEF/PySilCam', 'Yogayu/weibo-summary', 'adobe/antialiased-cnns', 'aldro61/kover', 'aquaskyline/Clairvoyante', 'bab2min/tomotopy', 'berkgulay/WeatherPredictionFromImage', 'bjoernkarmann/project_alias', 'devcongress/slackbot', 'neurodata/graspy', 'nnsuite/nnstreamer', 'opencv/training_toolbox_caffe', 'pangeo-data/pangeo-binder', 'richemslie/galvanise_zero', 'vc1492a/PyNomaly', 'wooorm/franc']
# l_tool_plus=['Aayush-Ankit/puma-simulator', 'BrikerMan/Kashgari', 'RenatoGeh/gospn', 'ThoughtWorksInc/DeepLearning.scala', 'gjy3035/C-3-Framework', 'keiffster/program-y', 'khurramjaved96/Recursive-CNNs', 'mapmeld/aoc_reply_dataset', 'nltk/nltk', 'pm4py/pm4py-source', 'rapidsai/cuml', 'siekmanj/sieknet', 'theopenconversationkit/tock', 'uds-lsv/TF-NNLM-TK']


class travis_repo_finder():
    def __init__(self, full_name,category):
        self.full_name = full_name
        self.category=category

    def find_travis(self):
        try:
            print(self.full_name)
            get_travis_repo(self.full_name)
            adoption=True
            # print('Adopted')
            return str(self.full_name+','+self.category+','+adoption.__str__()+'\n')
        except Exception as e:
            return str(self.full_name + ',' + self.category + ',' + False.__str__()+'\n')
            pass

NUM_CORE = mp.cpu_count()

def worker(arg):
    obj= arg
    return obj.find_travis()

if __name__ == "__main__":
    start_time_all = time.perf_counter()
    # applied=pd.read_csv('Applied_transition_with_problem.csv')
    # f_applied = open('../../CSV Outputs/applied_travis_api_2_08_13_2021.csv', 'w')
    # f_applied.write('ProjectName,Category')
    # f_applied.write('\n')

    output=open('travis-adoption-nonml.csv','w+')
    output.write('ProjectName,Type,TravisAPIAdoption\n')
    list_of_objects =[travis_repo_finder(el,'NonML') for el in df_nonml['ProjectName'].tolist()]
    print(len(list_of_objects))
    pool = mp.Pool(NUM_CORE)
    list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()
    for res in list_of_results:
        if res is None:
            continue
        output.write(res)
    # a=commit_failure_classifier('git://github.com/kakaobrain/torchgpipe.git','b3ae91c7e89644a73b9e9e44391d034bf746342f','4913a915adfd7f4b8fde66c3edfe01aebb929fb7').find_commit_fail_type()
    # print(a)
