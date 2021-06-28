import pandas as pd

import os

import time

class Project_stats_gen():
    def __init__(self, project,type):
        self.project = project
        self.type=type
        self.result = ""

    def process_csv(self):
        print('Processing stats of '+self.project+' type '+self.type)
        try:
            project_csv=pd.read_csv('Project Stats Year/'+self.type+'/'+self.project)
        except Exception as e:
            return str(self.project+','+self.type+',0,0,0,0,0')
        builds_states=project_csv['BuildState'].to_list()
        total_number_of_builds=len(builds_states)
        if total_number_of_builds == 0:
            print('no builds during period')
            return str(self.project+','+self.type+',0,0,0,0,0')
        total_number_of_passed_builds=len([x for x in builds_states if x =="passed"])
        total_number_of_failed_builds=len([x for x in builds_states if x =="failed"])
        total_number_of_errored_builds=len([x for x in builds_states if x =="errored"])
        total_number_of_canceled_builds=len([x for x in builds_states if x =="canceled"])
        return str(self.project + ',' + self.type + ','+str(total_number_of_builds)+','+str(total_number_of_passed_builds)+','+str(total_number_of_failed_builds)+','+str(total_number_of_errored_builds)+','+str(total_number_of_canceled_builds))



import multiprocessing as mp
NUM_CORE = 8 # set to the number of cores you want to use

def worker(arg):
    obj= arg
    return obj.process_csv()

if __name__ == "__main__":
    start_time_all = time.perf_counter()
    # log_files = os.listdir('FailedLogs-ForTesting')
    applied_project=os.listdir('../../Project Stats Month/Applied')
    tool_project=os.listdir('../../Project Stats Month/Tool')
    list_of_objects = [Project_stats_gen(i,'Applied') for i in applied_project]+[Project_stats_gen(i,'Tool') for i in tool_project]
    pool = mp.Pool(NUM_CORE)
    list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()

    csv_res = open('../../Project Stats Summary/projects-stats-year.csv', 'w+')
    csv_res.write('ProjectName,ProjectType,TotalNumberOfBuilds,TotalPassedBuilds,TotalFailedBuilds,TotalErroredBuilds,TotalCanceledBuilds')
    csv_res.write('\n')
    for line in list_of_results:
        csv_res.write(line)
        csv_res.write('\n')
    end_time_all = time.perf_counter()
    print(f"Execution Time : {end_time_all - start_time_all:0.6f}")


