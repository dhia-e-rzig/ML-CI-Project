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
        print('Processing stats of '+self.project+' type '+self.type)
        try:
            project_csv=pd.read_csv('../Project Stats Year/'+self.type+'/'+self.project+'/build_detailed_info.csv')
        except Exception as e :
            print(str(e))
            # exit()
            return
            # return s/tr(self.project)
        problem_mode=False
        nb_prob_builds_in_between=0
        date_first_fail=''

        builds_in_between_list=[]
        duration_in_between_list=[]
        project_csv=project_csv.loc[::-1].reset_index(drop = True)
        for index,row in project_csv.iterrows():
            if problem_mode == False and( row['BuildState'] == 'failed' or  row['BuildState'] == 'errored'):
                problem_mode=True
                try:
                    if date_first_fail =='':
                        date_first_fail= parser.parse(row['BuildCreationDate'])
                except  Exception as e:
                    print(e)
                    exit()
                continue
            if problem_mode and row['BuildState'] != 'passed' :
                nb_prob_builds_in_between+=1

            if problem_mode and row['BuildState'] == 'passed':
                builds_in_between_list.append(nb_prob_builds_in_between)
                try:
                    date_solution= parser.parse(row['BuildCreationDate'])
                    nb_days=(date_solution-date_first_fail).days
                except Exception as e:
                    print(date_first_fail)
                    print(e)
                    exit()
                duration_in_between_list.append(nb_days)
                nb_prob_builds_in_between=0
                date_first_fail=''
                problem_mode=False
        avg_builds_nb=0
        avg_builds_duration=0
        if len(builds_in_between_list) ==1 :
            avg_builds_nb=builds_in_between_list[0]
        elif len(builds_in_between_list) != 0 :
            avg_builds_nb=sum(builds_in_between_list)/len(builds_in_between_list)
        if len(duration_in_between_list)==1:
            avg_builds_duration=duration_in_between_list[0]
        elif len(duration_in_between_list) != 0:
            avg_builds_duration=sum(duration_in_between_list)/len(duration_in_between_list)
        if  avg_builds_nb==0 and     avg_builds_duration==0:
            return None
        else:
            return(self.project,self.type,avg_builds_nb,avg_builds_duration)
        # return str(self.project + ',' + self.type + ','+str(total_number_of_builds)+','+str(total_number_of_passed_builds)+','+str(total_number_of_failed_builds)+','+str(total_number_of_errored_builds)+','+str(total_number_of_canceled_builds))



import multiprocessing as mp
NUM_CORE = 8 # set to the number of cores you want to use

def worker(arg):
    obj= arg
    return obj.process_csv()

if __name__ == "__main__":
    start_time_all = time.perf_counter()
    # log_files = os.listdir('FailedLogs-ForTesting')
    applied_project=os.listdir('../Project Stats Year/Applied')
    tool_project=os.listdir('../Project Stats Year/Tool')
    list_of_objects = [Project_stats_gen(i,'Applied') for i in applied_project]+[Project_stats_gen(i,'Tool') for i in tool_project]
    pool = mp.Pool(NUM_CORE)
    list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()

    csv_res = open('../Project Stats Summary/failure_fix_nb_duration_2.csv', 'w+')
    csv_res.write('ProjectName,Type,AvgNbBuilds,AvgTimeforFix')
    csv_res.write('\n')
    for res in list_of_results:
        if res is None:
            continue
        type=res[1]
        nb_avg="{:.3f}".format(res[2])
        duratiob_avg="{:.3f}".format(res[3])
        csv_res.write(res[0]+','+type+','+nb_avg+','+duratiob_avg)
        csv_res.write('\n')
    end_time_all = time.perf_counter()
    print(f"Execution Time : {end_time_all - start_time_all:0.6f}")

