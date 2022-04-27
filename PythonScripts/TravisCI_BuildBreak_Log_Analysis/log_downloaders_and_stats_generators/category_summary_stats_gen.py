import pandas as pd

from os import path

import time

fail_ml_df=pd.read_csv('../../TravisCI_Builds_propertiesPerProjects/fail_ids_to_filter_ml.csv')
fail_nonml_df=pd.read_csv('../../TravisCI_Builds_propertiesPerProjects/fail_ids_to_filter_nonml.csv')
error_ml_df=pd.read_csv('../../TravisCI_Builds_propertiesPerProjects/error_ids_to_filter_ml.csv')
error_nonml_df=pd.read_csv('../../TravisCI_Builds_propertiesPerProjects/error_ids_to_filter_nonml.csv')

ids_to_ignore=fail_ml_df['id'].tolist()+fail_nonml_df['id'].tolist()+error_ml_df['id'].tolist()+error_nonml_df['id'].tolist()

class Project_stats_gen():
    def __init__(self, project,type):
        self.project = project
        self.type=type
        self.result = ""

    def process_csv(self):
        print('Processing stats of '+self.project+' type '+self.type)
        # path_1='../../../Project Stats Year/Applied/'+str(self.project).replace('/','_')+'/build_detailed_info.csv'
        # path_2='../../../Project Stats Year/Tool/'+str(self.project).replace('/','_')+'/build_detailed_info.csv'
        # if path.exists(path_1):
        #     path_csv=path_1
        # else:
        path_csv = '../../../Project Stats Year/'+str(self.type)+'/'+str(self.project).replace('/','_')+'/build_detailed_info.csv'
        try:
            project_csv=pd.read_csv(path_csv)

        except Exception as e:
            print('Exception')
            print(str(e))
            return str(self.project+','+self.type+',0,0,0,0,0')
        df=project_csv[~project_csv['BuildID'].isin(ids_to_ignore)]
        builds_states=df['BuildState'].to_list()
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
NUM_CORE = mp.cpu_count() # set to the number of cores you want to use
def worker(arg):
    obj= arg
    return obj.process_csv()

if __name__ == "__main__":
    start_time_all = time.perf_counter()
    # log_files = os.listdir('FailedLogs-ForTesting')
    # nonml_project=os.listdir('../../Project Stats Year/NonML')
    # tool_project=os.listdir('../../Project Stats Year/Tool')
    df_applied=pd.read_csv('../../../CSV Input - New/RQ3-RQ4-new.csv')
    df_nonml=pd.read_csv('../../../CSV Input - New/RQ3_4_NonML.csv')

    list_of_objects = [Project_stats_gen(row['RepoName'],row['RepoType']) for idx,row in df_applied.iterrows()]
                      # +[Project_stats_gen(i,'Tool') for i in tool_project]
    pool = mp.Pool(NUM_CORE)
    list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()

    csv_res = open('../../../Project Stats Summary/projects-stats-year-variable_ml_v8.csv', 'w+')
    csv_res.write('ProjectName,ProjectType,TotalNumberOfBuilds,TotalPassedBuilds,TotalFailedBuilds,TotalErroredBuilds,TotalCanceledBuilds')
    csv_res.write('\n')
    for line in list_of_results:
        csv_res.write(line)
        csv_res.write('\n')
    end_time_all = time.perf_counter()
    print(f"Execution Time : {end_time_all - start_time_all:0.6f}")

    start_time_all = time.perf_counter()
    list_of_objects = [Project_stats_gen(row['RepoName'],row['RepoType']) for idx,row in df_nonml.iterrows()]
                      # +[Project_stats_gen(i,'Tool') for i in tool_project]
    pool = mp.Pool(NUM_CORE)
    list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()

    csv_res = open('../../../Project Stats Summary/projects-stats-year-variable_nonml_v4.csv', 'w+')
    csv_res.write('ProjectName,ProjectType,TotalNumberOfBuilds,TotalPassedBuilds,TotalFailedBuilds,TotalErroredBuilds,TotalCanceledBuilds')
    csv_res.write('\n')
    for line in list_of_results:
        csv_res.write(line)
        csv_res.write('\n')
    end_time_all = time.perf_counter()
    print(f"Execution Time : {end_time_all - start_time_all:0.6f}")
