import pandas as pd
import random

from PythonScripts.Utils import Travis_Utils

df=pd.read_csv('../../CSV Inputs/python_projects_with_travis_info.csv')
List_of_tool_repos=df.loc[df['RepoType']=='Tool']['RepoName'].to_list()
List_of_applied_repos=df.loc[df['RepoType']=='Applied']['RepoName'].to_list()


random_tool_list = random.sample(List_of_tool_repos, 50)
random_applied_list = random.sample(List_of_applied_repos, 50)
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
        print('Processing jobs of '+self.project)
        try:
            travis_repo = Travis_Utils.get_travis_repo(self.project)
        except:
            return (self.project, self.type)
        build_page = travis_repo.get_builds()
        bool_build_next_page = True
        count_jobs_processed=0
        count_jobs_from_same_project_errored=0
        count_jobs_from_same_project_failed=0
        # list_failed_jobs=[]
        # list_errored_jobs=[]
        while (bool_build_next_page):
            # print(type(build_page))
            if (count_jobs_processed >= 300):
                return (self.project,self.type)
            bool_build_next_page = build_page.has_next_page()
            nb_jobs_from_same_project = 0
            for build in build_page.builds:
                if build.is_failed():
                    job_page = build.get_jobs()
                    bool_job_next_page = True
                    while (bool_job_next_page):
                        bool_job_next_page = job_page.has_next_page()
                        for job in job_page.jobs:
                            if (count_jobs_processed >= 300):
                                return (self.project, self.type)
                            count_jobs_processed+=1

                            if (count_jobs_from_same_project_errored > 50 or count_jobs_from_same_project_failed>50):
                                return (self.project, self.type)

                            if (job.is_failed(sync=True)):
                                output_str = job.get_log().content

                                if (output_str == "" or output_str is None):
                                    continue
                                else:
                                    with open('FailedJobs/'+str(self.type)+'/' + str(job.id) + '.txt', 'w+',
                                              encoding='utf-8') as file:
                                        file.write(output_str)
                                    count_jobs_from_same_project_failed+=1

                            if (job.is_errored(sync=True)):
                                output_str = job.get_log().content
                                if (output_str == "" or output_str == None):
                                    continue
                                else:
                                    with open('ErroredJobs/' + str(self.type) + '/' + str(job.id) + '.txt', 'w+',
                                              encoding='utf-8') as file:
                                        file.write(output_str)
                                    count_jobs_from_same_project_errored+=1

                        if bool_job_next_page:
                            job_page = job_page.next_page()
            if bool_build_next_page:
                build_page = build_page.next_page()
        return (self.project, self.type)


import multiprocessing as mp
NUM_CORE = 7
import time

def worker(arg):
    obj = arg
    return obj.download_job_logs()


if __name__ == "__main__":
    start_time_all = time.perf_counter()
    # log_files = os.listdir('FailedLogs-ForTesting')
    list_of_objects = [Project_Job_Log_Downloader_class(i,'Tool') for i in random_tool_list]+[Project_Job_Log_Downloader_class(i,'Applied') for i in random_applied_list]
    pool = mp.Pool(NUM_CORE)
    list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()

    csv_res = open('projects_chosen_50_50.csv', 'w+')
    csv_res.write('Project,Type')
    csv_res.write('\n')
    for line in list_of_results:
        csv_res.write(line[0]+','+line[1])
        csv_res.write('\n')
    end_time_all = time.perf_counter()
    print(f"Execution Time : {end_time_all - start_time_all:0.6f}")

