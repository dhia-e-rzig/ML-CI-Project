import pandas
import pandas as pd

import os
from dateutil import parser
import time

class Project_stats_gen():
    def __init__(self, project,type):
        self.project = project
        self.type=type
        self.result = ""

    def process_csv(self):
        # print('Processing stats of '+self.project)
        if self.type =='ML':
            try:
                project_csv=pd.read_csv('/home/umd-002677/PycharmProjects/ML-CI/Project Stats Year'+'/Applied/'+self.project+'/build_detailed_info.csv')
                failed_build=project_csv[project_csv['BuildState']=='failed']
                errored_build=project_csv[project_csv['BuildState']=='errored']
                return (len(project_csv.index),len(failed_build.index),len(errored_build.index))
            except  Exception as e1:
                # print(str(e1))
                try:
                    project_csv = pd.read_csv(
                        '/home/umd-002677/PycharmProjects/ML-CI/Project Stats Year' + '/Tool/' + self.project + '/build_detailed_info.csv')
                    failed_build = project_csv[project_csv['BuildState'] == 'failed']
                    errored_build = project_csv[project_csv['BuildState'] == 'errored']
                    return (len(project_csv.index),len(failed_build.index),len(errored_build.index))
                except Exception as e2:
                    print(str(e2))
                # exit()
                return (0,0,0)
        elif self.type =='NonML':
            try:
                project_csv=pd.read_csv('/home/umd-002677/PycharmProjects/ML-CI/Project Stats Year'+'/NonML/'+self.project+'/build_detailed_info.csv')
                failed_build = project_csv[project_csv['BuildState'] == 'failed']
                errored_build = project_csv[project_csv['BuildState'] == 'errored']
                return (len(project_csv.index), len(failed_build.index), len(errored_build.index))
            except Exception as e2:
                print(str(e2))
                return (0,0,0)
            # return s/tr(self.project)
        else:
            print('wrong type')
            return (0,0,0)

        # return str(self.project + ',' + self.type + ','+str(total_number_of_builds)+','+str(total_number_of_passed_builds)+','+str(total_number_of_failed_builds)+','+str(total_number_of_errored_builds)+','+str(total_number_of_canceled_builds))



import multiprocessing as mp
NUM_CORE = 8 # set to the number of cores you want to use

def worker(arg):
    obj= arg
    return obj.process_csv()

if __name__ == "__main__":
    start_time_all = time.perf_counter()
    # log_files = os.listdir('FailedLogs-ForTesting')
    df1=pandas.read_csv('../../CSV Input - New/RQ3-RQ4-new.csv')
    temp_list=df1['RepoName'].tolist()
    fil_list=[str(x).replace('/','_') for x in temp_list]
    # print(fil_list)
    # applied_project=os.listdir('D:/ML-CI/Project Stats Year/Applied')
    # print(applied_project)
    # exit()
    # tool_project=os.listdir('D:/ML-CI/Project Stats Year/Tool')
    list_of_objects = [Project_stats_gen(i,'ML') for i in fil_list]
    pool = mp.Pool(NUM_CORE)
    list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()
    # print(list_of_results)

    nb_builds_all = 0
    nb_builds_fail = 0
    nb_builds_error = 0
    for res in list_of_results:
        print(res)
        nb_builds_all += res[0]
        nb_builds_fail += res[1]
        nb_builds_error += res[2]
    print('total number of ML builds')
    print(nb_builds_all)
    print('total number of failed ML builds')
    print(nb_builds_fail)
    print('total number of  errored ML builds')
    print(nb_builds_error)

    end_time_all = time.perf_counter()
    print(f"Execution Time : {end_time_all - start_time_all:0.6f}")
    # exit()
    df2=pandas.read_csv('../../CSV Input - New/RQ3_4_NonML.csv')
    temp_list=df2['RepoName'].tolist()
    fil_list=[str(x).replace('/','_') for x in temp_list]
    # print(fil_list)
    # applied_project=os.listdir('D:/ML-CI/Project Stats Year/Applied')
    # print(applied_project)
    # exit()
    # tool_project=os.listdir('D:/ML-CI/Project Stats Year/Tool')
    list_of_objects = [Project_stats_gen(i,'NonML') for i in fil_list]
    pool = mp.Pool(NUM_CORE)
    list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()
    # print(list_of_results)
    nb_builds_all=0
    nb_builds_fail=0
    nb_builds_error=0
    for res in list_of_results:
        print(res)
        nb_builds_all+=res[0]
        nb_builds_fail+=res[1]
        nb_builds_error+=res[2]
    print('total number of Non-ML builds')
    print(nb_builds_all)
    print('total number of failed Non-ML builds')
    print(nb_builds_fail)
    print('total number of  errored Non-ML builds')
    print(nb_builds_error)
    end_time_all = time.perf_counter()
    print(f"Execution Time : {end_time_all - start_time_all:0.6f}")
