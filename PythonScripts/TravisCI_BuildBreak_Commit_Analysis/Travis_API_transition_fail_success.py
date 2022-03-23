import collections
import datetime

from github import Github
from pydriller import Repository, Git
import pandas as pd
from PythonScripts.Utils import Travis_Utils
df=pd.read_csv('repeat_stats.csv')
import os
import sys
import failure_classifier
import error_classifier
from PythonScripts.Utils import Github_Utils as GHUtils


List_of_tool_repos=df.loc[df['RepoType']=='Tool']['RepoName'].to_list()
List_of_applied_repos=df.loc[df['RepoType']=='Applied']['RepoName'].to_list()

gh= Github(GHUtils.get_github_token())

class Project_State_Processor_class():
    def __init__(self, project,type):
        self.project = project
        self.type = type

    def find_build_transitions(self):
        start_time_all = time.perf_counter()
        project=self.project
        return_tups_list=[]
        script_path= '../../Project Stats Year'
        project_stats_path = os.path.join(script_path, str(self.type)+'/' + str(project).replace('/','_'))
        problem_type_list = []
        problem_type_main = 'Unknown'
        Notes=''
        try:
            df=pd.read_csv(project_stats_path+'/build_detailed_info.csv')
            local_repo = Git(
                'D:/PhD Work/repos/' + str(self.type).lower() + '/' + str(self.project))
            gh_repo = gh.get_repo(project)
            url = gh_repo.git_url
            df=df[::-1].reset_index(drop = True)
            prev_state=''
            prev_build_id=''
            for index,row in df.iterrows():
                if prev_state == '':
                    prev_state=row['BuildState']
                    prev_build_id=row['BuildID']
                    continue
                elif row['BuildState']=='passed' and prev_state != row['BuildState']:
                    problem_build_state=prev_state
                    try:
                        prev_build=Travis_Utils.get_travis_build(prev_build_id)
                        if prev_build.is_incomplete():
                            prev_build=prev_build.get_complete()
                        curr_build=Travis_Utils.get_travis_build(row['BuildID'])
                        if curr_build.is_incomplete():
                            curr_build=curr_build.get_complete()
                        prob_commit=prev_build.commit.sha
                        sol_commit=curr_build.commit.sha
                        prob_commit_jobs=prev_build.get_jobs().jobs
                        try:
                            local_solution_commit=local_repo.get_commit(sol_commit)
                            if local_solution_commit is None:
                                remote_solution_commit=gh_repo.get_commit(sol_commit)
                                trav_file=[f for f in remote_solution_commit.files if '.travis.yml' in f.filename]
                                if len(trav_file) ==0:
                                    continue
                            else:
                                mod_files=local_solution_commit.modified_files
                                trav_file = [f for f in mod_files if '.travis.yml' in f.filename]
                                if len(trav_file) == 0:
                                    continue
                        except Exception as e:
                            try:
                                remote_solution_commit = gh_repo.get_commit(sol_commit)
                                trav_file = [f for f in remote_solution_commit.files if '.travis.yml' in f.filename]
                                if len(trav_file) == 0:
                                    continue
                            except Exception as e:
                                print(e)
                                continue
                    except Exception as e:
                        with open("travis_api_transition_err.txt", "a+") as error:
                            error.write(project + ',' + str(e))
                            error.write('\n')
                            print(project + "," + str(e))
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            print(exc_type, fname, exc_tb.tb_lineno)
                            continue
                    nb_jobs_processed=0
                    for job in prob_commit_jobs:
                        job_id=job.id
                        if(job.state!=prev_build.state):
                            continue
                        nb_jobs_processed+=1
                        job_local_path=project_stats_path+'/job_logs/'+str(job_id)+'.txt'
                        if(not os.path.exists(job_local_path)):
                            try:
                                job_content=job.get_log().content
                                if job_content is None or job_content =="":
                                    continue
                                with open('commits_jobs_prob_for_transition/'+str(job.state)+"_"+str(prev_build_id)+"_"+str(prob_commit)+".txt",'w') as f:
                                    f.write(job_content)
                                job_local_path='commits_jobs_prob_for_transition/'+str(job.state)+"_"+str(prev_build_id)+"_"+str(prob_commit)+".txt"
                            except Exception as e:
                                print(e)
                                continue
                        if(job.state=="errored"):
                            analysis_results = error_classifier.Log_failure_classifier(job_local_path).process_file_with_regexes()
                            error_types = analysis_results[0]
                            # print(analysis_results)
                            if error_types.split(',')[1] == 'True':
                                problem_type_list.append('FailMarkedAsError')
                            elif error_types.split(',')[2] == 'True':
                                problem_type_list.append('ScriptError')
                            elif error_types.split(',')[3] == 'True':
                                problem_type_list.append('BuildDependencyError')
                            elif error_types.split(',')[4] == 'True':
                                problem_type_list.append('TravisError')
                        else:
                            analysis_results = failure_classifier.Log_failure_classifier(
                                job_local_path).process_file_with_regexes()
                            fail_types = analysis_results[0]
                            # print(fail_types.split(','))
                            if fail_types.split(',')[1] == 'True':
                                problem_type_list.append('TestFail')

                            elif fail_types.split(',')[2] == 'True':
                                problem_type_list.append('BuildError')

                            elif fail_types.split(',')[3] == 'True':
                                problem_type_list.append('TestError')

                            elif fail_types.split(',')[4] == 'True':
                                problem_type_list.append('CodeAnalysisError')

                            elif fail_types.split(',')[5] == 'True':
                                problem_type_list.append('TravisFail')

                            elif fail_types.split(',')[6] == 'True':
                                problem_type_list.append('DeploymentError')
                    if len(problem_type_list) != 0:
                        frequency = collections.Counter(problem_type_list)
                        try:
                            MaxKey = max(frequency, key=frequency.get)
                            problem_type_main = MaxKey
                        except:
                            pass
                    if len(problem_type_list) == 0  and nb_jobs_processed !=0:
                        problem_type_main='Undetected'
                    return_tups_list.append((
                        url, prob_commit, sol_commit, problem_type_main, problem_type_list,
                        problem_build_state, Notes))
                else:
                    continue
        except Exception as e:
            with open("travis_api_transition_err.txt", "a+") as error:
                error.write(project + ',' + str(e))
                error.write('\n')
                print(project + "," + str(e))
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)

        end_time_all = time.perf_counter()
        print("Execution Time for "+project+f" : {end_time_all - start_time_all:0.6f}")
        return return_tups_list
import multiprocessing as mp
NUM_CORE = 8
import time

def worker(arg):
    obj= arg
    return obj.find_build_transitions()

if __name__ == "__main__":
    start_time_all = time.perf_counter()
    # log_files = os.listdir('FailedLogs-ForTesting')

    list_of_objects = [Project_State_Processor_class(i,'Applied') for i in List_of_applied_repos]
    pool = mp.Pool(NUM_CORE)
    list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()

    # (url, prob_commit, sol_commit, problem_type_main, problem_type_list, problem_build_state, Notes)
    with open('additional_stats_with_prob_applied','w+') as f:
        f.write('ProjectGitRepo,Failed-ErrorredCommitID,FixCommitID,MainProblem,AllProblems,ProblemBuildState,Notes')
        for list_of_tups in list_of_results:
            if len(list_of_tups) == 0:
                continue
            print(list_of_tups)
            for tup in list_of_tups:
                f.write(str(tup[0])+','+str(tup[1])+','+str(tup[2])+','+str(tup[3])+','+str(tup[4]).replace(',',';')+','+str(tup[5])+','+str(tup[6]))
                f.write('\n')
    list_of_objects =[Project_State_Processor_class(i, 'Tool') for i in List_of_tool_repos]
    pool = mp.Pool(NUM_CORE)
    list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()
    # (url, prob_commit, sol_commit, problem_type_main, problem_type_list, problem_build_state, Notes)
    with open('additional_stats_with_prob_tool', 'w+') as f:
        for list_of_tups in list_of_results:
            if len(list_of_tups)==0:
                continue
            for tup in list_of_tups:
                f.write(str(tup[0])+','+str(tup[1])+','+str(tup[2])+','+str(tup[3])+','+str(tup[4]).replace(',',';')+','+str(tup[5])+','+str(tup[6]))
                f.write('\n')
    end_time_all = time.perf_counter()
    print(f"Execution Time for all : {end_time_all - start_time_all:0.6f}")
