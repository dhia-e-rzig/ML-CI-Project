from pprint import pprint

import pandas as pd
import random
import _thread
import threading
from contextlib import contextmanager
from datetime import datetime, date, time, timedelta

from PythonScripts.Utils import Travis_Utils

class TimeoutException(Exception):
    def __init__(self, msg=''):
        self.msg = msg


@contextmanager
def time_limit(seconds, msg=''):
    timer = threading.Timer(seconds, lambda: _thread.interrupt_main())
    timer.start()
    try:
        yield
    except KeyboardInterrupt:
        raise TimeoutException("Timed out for operation {}".format(msg))
    finally:
        timer.cancel()

df=pd.read_csv('../../CSV Input - New/RQ3_4_NonML.csv')
non_ml_list=df['RepoName']
# pprint(df['ML-AI'].tolist())
# List_of_tool_repos=df.loc[ (df['RepoType']=='Tool') & (df['ML-AI']=='Yes')]['RepoName'].to_list()
# pprint(List_of_tool_repos)
# List_of_applied_repos=df.loc[(df['RepoType']=='Applied') & (df['ML-AI']=='Yes') ]['RepoName'].to_list()
# pprint(List_of_applied_repos)
# df_devops_class=pd.read_csv('../../CSV Inputs/devops project type/All_projects_classification.csv')

# List_of_tool_withDeploy=[ x for x in List_of_tool_repos if df_devops_class[df_devops_class['ProjectName']==x]['DeploymentAutomation'].tolist()[0] == 1 ]
# pprint(List_of_tool_withDeploy)
# List_of_applied_withDeploy=[ x for x in List_of_applied_repos if df_devops_class[df_devops_class['ProjectName']==x]['DeploymentAutomation'].tolist()[0] == 1 ]
# pprint(List_of_applied_withDeploy)
# exit()
# number_of_rand_projects=min(len(List_of_tool_withDeploy),len(List_of_applied_withDeploy))//2

# pprint('number of random projects selected is: '+str(number_of_rand_projects))

# random_tool_list = random.sample(List_of_tool_repos, number_of_rand_projects)
# random_applied_list = random.sample(List_of_applied_repos, number_of_rand_projects)


# random_applied_list=List_of_applied_repos[random_applied_range]
# random_tool_list=List_of_tool_repos[random_tool_range]
# list_failed_jobs=[]
# list_errored_jobs=[]
# tool_failed_jobs=[]
# applied_failed_jobs=[]
# tool_errored_jobs=[]
# applied_errored_jobs=[]
# #
# projects_chosen_list=open('projects_chosen_50_50.csv','w')
# projects_chosen_list.write('RepoName,RepoType')





class Project_Job_Log_Downloader_class():
    def __init__(self, project,type):
        self.project = project
        self.type = type
        self.result = ""
    def download_job_logs(self):
        first_build_before_cutoff_found=False
        try:
            with time_limit(600):
                print('Processing jobs of '+self.project)
                try:
                    travis_repo = Travis_Utils.get_travis_repo(self.project)
                except:
                    return (self.project, self.type)
                build_page = travis_repo.get_builds()
                bool_build_next_page = True
                count_jobs_processed=0.
                while (bool_build_next_page):
                    bool_build_next_page = build_page.has_next_page()
                    for build in build_page.builds:
                        # if(build.started_at.date() > )
                        if build.is_failed():
                            job_page = build.get_jobs()
                            bool_job_next_page = True
                            while (bool_job_next_page):
                                bool_job_next_page = job_page.has_next_page()
                                for job in job_page.jobs:
                                    count_jobs_processed+=1
                                    if (job.is_failed(sync=True)):
                                        try:
                                            output_str = job.get_log().content
                                        except Exception:
                                            continue
                                        if (output_str == "" or output_str is None):
                                            continue
                                        else:
                                                with open('../../FailedJobs/'+str(self.type)+'/' + str(job.id) + '.txt', 'w+',
                                                          encoding='utf-8') as file:
                                                    file.write(output_str)
                                    if (job.is_errored(sync=True)):
                                        output_str = job.get_log().content
                                        if (output_str == "" or output_str == None):
                                            continue
                                        else:
                                                with open('../../ErroredJobs/' + str(self.type) + '/' + str(job.id) + '.txt', 'w+',
                                                          encoding='utf-8') as file:
                                                    file.write(output_str)
                                if bool_job_next_page:
                                    job_page = job_page.next_page()
                    if bool_build_next_page:
                        build_page = build_page.next_page()
                return (self.project, self.type)
        except Exception as e:
            print(e)
            print('time limit exceded for project: ' + self.project)
        return (self.project, self.type)



import multiprocessing as mp
NUM_CORE = mp.cpu_count()
import time

def worker(arg):
    obj = arg
    return obj.download_job_logs()


if __name__ == "__main__":
    start_time_all = time.perf_counter()
    # log_files = os.listdir('FailedLogs-ForTesting')

    list_of_objects = [Project_Job_Log_Downloader_class(i,'nonML') for i in non_ml_list]
    pool = mp.Pool(NUM_CORE)
    list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()

    csv_res = open('log_download.csv', 'w+')
    # csv_res.write('Project,Type')
    # csv_res.write('\n')
    for line in list_of_results:
        csv_res.write(line[0]+','+line[1]+',done')
        csv_res.write('\n')
    end_time_all = time.perf_counter()
    print(f"Execution Time : {end_time_all - start_time_all:0.6f}")

