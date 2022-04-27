import pandas
import pandas as pd

import os
from dateutil import parser
import time
from PythonScripts.Utils.Travis_Utils import get_travis_build


class Project_fail_error_extractor():
    def __init__(self, project,type):
        self.project = project
        self.type=type
        self.result = ""

    def process_csv(self):
        print('Processing stats of '+self.project)
        if self.type =='ML':
            try:
                project_csv=pd.read_csv('/home/umd-002677/PycharmProjects/ML-CI/Project Stats Year'+'/Applied/'+self.project+'/build_detailed_info.csv')
                failed_build=project_csv[project_csv['BuildState']=='failed']
                failed_list=[]
                errored_list=[]
                for tuple in failed_build.itertuples():
                    failed_list.append(tuple[1])
                errored_build=project_csv[project_csv['BuildState']=='errored']
                for tuple in errored_build.itertuples():
                    errored_list.append(tuple[1])
                return (failed_list,errored_list)
            except  Exception as e1:
                # print(str(e1))
                try:
                    project_csv = pd.read_csv(
                        '/home/umd-002677/PycharmProjects/ML-CI/Project Stats Year' + '/Tool/' + self.project + '/build_detailed_info.csv')
                    failed_list = []
                    errored_list = []
                    failed_build = project_csv[project_csv['BuildState'] == 'failed']
                    for tuple in failed_build.itertuples():
                        failed_list.append(tuple[1])
                    errored_build = project_csv[project_csv['BuildState'] == 'errored']
                    for tuple in errored_build.itertuples():
                        errored_list.append(tuple[1])
                    return (failed_list,errored_list)
                except Exception as e2:
                    print(str(e2))
                # exit()
                return ([],[])
        elif self.type =='NonML':
            try:
                project_csv=pd.read_csv('/home/umd-002677/PycharmProjects/ML-CI/Project Stats Year'+'/NonML/'+self.project+'/build_detailed_info.csv')
                failed_build = project_csv[project_csv['BuildState'] == 'failed']
                errored_build = project_csv[project_csv['BuildState'] == 'errored']
                failed_list = []
                errored_list = []
                for tuple in failed_build.itertuples():
                    failed_list.append(tuple[1])
                for tuple in errored_build.itertuples():
                    errored_list.append(tuple[1])
                return (failed_list, errored_list)
            except Exception as e2:
                print(str(e2))
                return ([],[])
            # return s/tr(self.project)
        else:
            print('wrong type')
            return  ([],[])

        # return str(self.project + ',' + self.type + ','+str(total_number_of_builds)+','+str(total_number_of_passed_builds)+','+str(total_number_of_failed_builds)+','+str(total_number_of_errored_builds)+','+str(total_number_of_canceled_builds))


class Project_pass_extractor():
    def __init__(self, project,type):
        self.project = project
        self.type=type
        self.result = ""

    def process_csv(self):
        # print('Processing stats of '+self.project)
        if self.type =='ML':
            try:
                project_csv=pd.read_csv('/home/umd-002677/PycharmProjects/ML-CI/Project Stats Year'+'/Applied/'+self.project+'/build_detailed_info.csv')
                failed_build=project_csv[project_csv['BuildState']=='passed']
                failed_list=[]
                # errored_list=[]
                for tuple in failed_build.itertuples():
                    failed_list.append(tuple[1])
                # errored_build=project_csv[project_csv['BuildState']=='errored']
                # for tuple in errored_build.itertuples():
                #     errored_list.append(tuple[1])
                return (failed_list)
            except  Exception as e1:
                # print(str(e1))
                try:
                    project_csv = pd.read_csv(
                        '/home/umd-002677/PycharmProjects/ML-CI/Project Stats Year' + '/Tool/' + self.project + '/build_detailed_info.csv')
                    failed_list = []

                    failed_build = project_csv[project_csv['BuildState'] == 'passed']
                    for tuple in failed_build.itertuples():
                        failed_list.append(tuple[1])
                    # errored_build = project_csv[project_csv['BuildState'] == 'errored']
                    # for tuple in errored_build.itertuples():
                    #     errored_list.append(tuple[1])
                    return (failed_list)
                except Exception as e2:
                    print(str(e2))
                # exit()
                return ([])
        elif self.type =='NonML':
            try:
                project_csv=pd.read_csv('/home/umd-002677/PycharmProjects/ML-CI/Project Stats Year'+'/NonML/'+self.project+'/build_detailed_info.csv')
                failed_build = project_csv[project_csv['BuildState'] == 'passed']
                # errored_build = project_csv[project_csv['BuildState'] == 'errored']
                failed_list = []
                # errored_list = []
                for tuple in failed_build.itertuples():
                    failed_list.append(tuple[1])
                # for tuple in errored_build.itertuples():
                #     errored_list.append(tuple[1])
                return (failed_list)
            except Exception as e2:
                print(str(e2))
                return ([])
            # return s/tr(self.project)
        else:
            print('wrong type')
            return  ([])

        # return str(self.project + ',' + self.type + ','+str(total_number_of_builds)+','+str(total_number_of_passed_builds)+','+str(total_number_of_failed_builds)+','+str(total_number_of_errored_builds)+','+str(total_number_of_canceled_builds))


import multiprocessing as mp
NUM_CORE = 8 # set to the number of cores you want to use

def worker(arg):
    obj= arg
    return obj.process_csv()

if __name__ == "__main__":
    # start_time_all = time.perf_counter()
    # # log_files = os.listdir('FailedLogs-ForTesting')
    # df1=pandas.read_csv('../../CSV Input - New/RQ3-RQ4-new.csv')
    # temp_list=df1['RepoName'].tolist()
    # fil_list=[str(x).replace('/','_') for x in temp_list]
    # # print(fil_list)
    # # applied_project=os.listdir('D:/ML-CI/Project Stats Year/Applied')
    # # print(applied_project)
    # # exit()
    # # tool_project=os.listdir('D:/ML-CI/Project Stats Year/Tool')
    # list_of_objects = [Project_pass_extractor(i, 'ML') for i in fil_list]
    # pool = mp.Pool(NUM_CORE)
    # list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    # pool.close()
    # pool.join()
    # # print(list_of_results)
    # #
    # # nb_builds_all = 0
    # # nb_builds_fail = 0
    # # nb_builds_error = 0
    # # for res in list_of_results:
    # #     nb_builds_all += res[0]
    # #     nb_builds_fail += res[1]
    # #     nb_builds_error += res[2]
    # # print('total number of ML builds')
    # # print(nb_builds_all)
    # # print('total number of failed ML builds')
    # # print(nb_builds_fail)
    # # print('total number of  errored ML builds')
    # # print(nb_builds_error)
    # end_time_all = time.perf_counter()
    # print(f"Execution Time : {end_time_all - start_time_all:0.6f}")
    # # exit()
    # builds_fail_list=[]
    # builds_fail_to_rem_list=[]
    # builds_error_list=[]
    # builds_error_to_rem_list=[]
    # excep_out=open('Ml-exceptions.txt','w+')
    # for res in list_of_results:
    #     builds_fail_list += res
    #     # builds_error_list += res[1]
    # for fail_build in builds_fail_list:
    #     try:
    #         # print(fail_build)
    #         build = get_travis_build(fail_build)
    #         print(fail_build)
    #         if build.event_type == 'cron' or build.event_type == 'api':
    #             builds_fail_to_rem_list.append(fail_build)
    #         elif build.tag is not None:
    #             builds_fail_to_rem_list.append(fail_build)
    #     except Exception as e:
    #         excep_out.write(str(e))
    #         excep_out.write('\n')
    #         continue
    # # for error_build in builds_error_list:
    # #     try:
    # #         # print(fail_build)
    # #         build = get_travis_build(error_build)
    # #         print(error_build)
    # #         if build.event_type == 'cron' or build.event_type == 'api':
    # #             builds_error_to_rem_list.append(error_build)
    # #         elif build.tag is not None:
    # #             builds_error_to_rem_list.append(error_build)
    # #     except  Exception as e:
    # #         excep_out.write(str(e))
    # #         excep_out.write('\n')
    # #         continue
    #
    # csv_out=open('pass_ids_to_filter_ml.csv','w+')
    # for build_id in builds_fail_to_rem_list:
    #     csv_out.write(str(build_id))
    #     csv_out.write('\n')
    # csv_out=open('error_ids_to_filter_ml.csv','w+')
    # for build_id in builds_error_to_rem_list:
    #     csv_out.write(str(build_id))
    #     csv_out.write('\n')

    df2=pandas.read_csv('../../CSV Input - New/RQ3_4_NonML.csv')
    temp_list=df2['RepoName'].tolist()
    fil_list=[str(x).replace('/','_') for x in temp_list]
    # print(fil_list)
    # applied_project=os.listdir('D:/ML-CI/Project Stats Year/Applied')
    # print(applied_project)
    # exit()
    # tool_project=os.listdir('D:/ML-CI/Project Stats Year/Tool')
    list_of_objects = [Project_pass_extractor(i, 'NonML') for i in fil_list]
    pool = mp.Pool(NUM_CORE)
    list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()
    # print(list_of_results)
    # exit()
    builds_fail_list = []
    builds_fail_to_rem_list = []
    builds_error_list = []
    builds_error_to_rem_list = []
    for res in list_of_results:
        builds_fail_list += res
        # builds_error_list += res[1]


    excep_out=open('NonMl-exceptions.txt','w+')
    for fail_build in builds_fail_list:
        try:
            # print(fail_build)
            build = get_travis_build(fail_build)
            print(fail_build)
            if build.event_type == 'cron' or build.event_type == 'api':
                builds_fail_to_rem_list.append(fail_build)
            elif build.tag is not None:
                builds_fail_to_rem_list.append(fail_build)
        except Exception as e:
            excep_out.write(str(e))
            excep_out.write('\n')
            continue
    # for error_build in builds_error_list:
    #     try:
    #         # print(fail_build)
    #         build = get_travis_build(error_build)
    #         print(error_build)
    #         if build.event_type == 'cron' or build.event_type == 'api':
    #             builds_error_to_rem_list.append(error_build)
    #         elif build.tag is not None:
    #             builds_error_to_rem_list.append(error_build)
    #     except  Exception as e:
    #         excep_out.write(str(e))
    #         excep_out.write('\n')
    #         continue

    csv_out = open('pass_ids_to_filter_nonml.csv', 'w+')
    for build_id in builds_fail_to_rem_list:
        csv_out.write(str(build_id))
        csv_out.write('\n')
    # csv_out = open('error_ids_to_filter_nonml.csv', 'w+')
    # for build_id in builds_error_to_rem_list:
    #     csv_out.write(str(build_id))
    #     csv_out.write('\n')
