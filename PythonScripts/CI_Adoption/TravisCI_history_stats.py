import os
import sys

from ghapi.all import *
from github import Github

from PythonScripts.Utils import Github_Utils as GHU
import pandas as pd
import time
from PythonScripts.Utils.Travis_Utils import get_travis_repo
import multiprocessing as mp
from dateutil import parser

all_travis_projects_df=pd.read_csv('..\\..\\CSV Outputs\\allprojects_travis_api_2_08_13_2021.csv')

class travis_repo_finder():
    def __init__(self, full_name,category):
        self.full_name = full_name
        self.category=category

    def find_travis(self):
        try:
            a=get_travis_repo(self.full_name)
            first_page=a.get_builds().builds
            last_build = first_page[0]
            i=0
            print(last_build.started_at)
            while last_build.started_at is None:
                last_build = first_page[i]
                i+=1
            last_page=a.get_builds().last_page().builds
            first_build=last_page[-1]
            i=-1
            while first_build.started_at is None:
                first_build = last_page[i]
                i -= 1
            total_run_count=int(last_build.number) - int(first_build.number) + 1
            end_date = last_build.started_at
            start_date = first_build.started_at
            delta_diff=end_date-start_date
            days = int(delta_diff.days)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('EXCEPTION: ' + self.full_name)
            print(exc_type, fname, exc_tb.tb_lineno)
            start_date = "Error"
            end_date = "Error"
            days = 0
            total_run_count = 0
        return (self.full_name, self.category, start_date, end_date, total_run_count, days)

NUM_CORE = mp.cpu_count()

def worker_1(arg):
    obj= arg
    return obj.find_travis()


if __name__ == "__main__":
    start_time_all = time.perf_counter()
    # applied=pd.read_csv('Applied_transition_with_problem.csv')
    f_githubA_stats = open('Travisci_history_stats.csv', 'w+')
    list_of_objects = [travis_repo_finder(row['ProjectName'],row['Category']) for index,row in all_travis_projects_df.iterrows()]
    pool = mp.Pool(NUM_CORE)
    list_of_results = pool.map(worker_1, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()
    f_githubA_stats.write('ProjectName,ProjectType,StartDate,EndDate,TotalRuns,DaysOfCIActivity\n')
    for res in list_of_results:
        print(res)
        if res is None:
            continue
        f_githubA_stats.write(str(res[0])+','+str(res[1])+','+str(res[2])+','+str(res[3])+','+str(res[4])+','+str(res[5])+'\n')

