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

# all_travis_projects_df=pd.read_csv('..\\..\\CSV Outputs\\allprojects_travis_api_2_08_13_2021.csv')
g=Github(GHU.get_github_token())

# df_temp=pd.read_csv('CI_adoption_tool.csv')
# githubA_tool_projects=df_temp[df_temp['GithubA']==False]['projectName'].to_list()
# df_temp=pd.read_csv('CI_adoption_applied.csv')
# githubA_applied_projects=df_temp[df_temp['GithubA']==False]['projectName'].to_list()

non_ml_projects=pd.read_csv('../../CSV Input - New/NonML-classification.csv')


class githubA_repo_finder():
    def __init__(self, full_name,category):
        self.full_name = full_name
        self.category=category

    def find_githubA(self):
        done=False
        start_date = "None"
        end_date = "None"
        days = 0
        total_run_count = 0
        creation_dates_all = []
        while (not done):
            try:
                a=GhApi(owner=str(self.full_name).split('/')[0],repo=str(self.full_name).split('/')[1],token=GHU.get_github_token())
                # b=a.actions.list_repo_workflows(owner=str(self.full_name).split('/')[0],repo=str(self.full_name).split('/')[1])
                # workflows=str(b).split('- \n')
                # splits= [ x.split('\n')[0] for x in workflows]
                # print(splits)
                # id_strings=[f for f in splits if '- id:' in str(f) ]
                # print(id_strings)
                # list_ids=[int(''.join(i for i in f if i.isdigit())) for f in id_strings ]
                # for id in list_ids:
                print(self.full_name)
                # runs = a.actions.list_workflow_runs_for_repo(owner=str(self.full_name).split('/')[0],
                #                                              repo=str(self.full_name).split('/')[1],per_page=1)
                # skip_dates=False
                # if total_run_count ==0:
                    # print(runs)
                    # print(self.full_name)
                    # skip_dates=True
                # if not skip_dates:
                pages=paged(a.actions.list_workflow_runs_for_repo,owner=str(self.full_name).split('/')[0],repo=str(self.full_name).split('/')[1],per_page=100)
                total_runs_found=False
                prev_page=''
                for page in pages:
                    if prev_page=='':
                        prev_page=page
                    if not total_runs_found:
                        splits = str(page).split('\n')
                        total_run_count = int(''.join(i for i in splits[0] if i.isdigit()))
                        total_runs_found=True
                        if total_run_count == 0:
                            start_date = "None"
                            end_date = "None"
                            days = 0
                            done = True
                            break
                        else:
                            creation_dates_str = [f for f in splits if 'created_at' in f]
                            creation_dates_all.extend(creation_dates_str)
                    if str(page).endswith('workflow_runs:'):
                        splits = str(prev_page).split('\n')
                        creation_dates_str = [f for f in splits if 'created_at' in f]
                        creation_dates_all.extend(creation_dates_str)
                        break
                    prev_page=page
                if total_run_count !=0:
                    end_date= parser.parse(creation_dates_all[0].split('created_at:')[1].strip())
                    start_date= parser.parse(creation_dates_all[-1].split('created_at:')[1].strip())
                    delta_diff = end_date - start_date
                    days=int(delta_diff.days)
                    done=True
            except Exception as e:
                if GHU.is_over_core_rate(g) or "API rate limit exceeded" in str(e) or "403" in str(e):
                    print(e)
                    GHU.sleep_until_core_rate_reset(g)
                else:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print('EXCEPTION'+self.full_name)
                    print(exc_type, fname, exc_tb.tb_lineno)
                    start_date="Error"
                    end_date="Error"
                    days=0
                    total_run_count=0
                    done=True
        return(self.full_name,self.category,start_date,end_date,total_run_count,days)



NUM_CORE = mp.cpu_count()

def worker_1(arg):
    obj= arg
    return obj.find_travis()


def worker_2(arg):
    obj= arg
    return obj.find_githubA()

if __name__ == "__main__":
    start_time_all = time.perf_counter()
    # applied=pd.read_csv('Applied_transition_with_problem.csv')
    f_githubA_stats = open('githubActions_stats_nonml.csv', 'w+')
    list_of_objects = [githubA_repo_finder(project,'NonML') for project in non_ml_projects['ProjectName'].tolist()]
    # pool = mp.Pool(NUM_CORE)
    # list_of_results = pool.map(worker_2, ((obj) for obj in list_of_objects))
    # pool.close()
    # pool.join()
    f_githubA_stats.write('ProjectName,ProjectType,StartDate,EndDate,TotalRuns,DaysOfCIActivity\n')
    for object in list_of_objects:
        res=object.find_githubA()
        print(res)
        if res is None:
            continue
        f_githubA_stats.write(str(res[0])+','+str(res[1])+','+str(res[2])+','+str(res[3])+','+str(res[4])+','+str(res[5])+'\n')

