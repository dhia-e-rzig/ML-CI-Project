import collections
import sys
import os
from pprint import pprint

import failure_classifiers.failure_classifier as failure_classifier
import error_classifier
import pandas as pd
import time
import PythonScripts.Utils.Travis_Utils as Travis_Utils
import multiprocessing as mp
import git

class commit_failure_classifier():
    def __init__(self, git_uri,prob_commit,fix_commit,build_prob,type):
        self.git_uri = git_uri
        self.prob_commit=prob_commit
        self.fix_commit=fix_commit
        self.type=type
        self.build_prob=build_prob

    def find_commit_fil_type_local(self):
        # The path for listing items
        path = './commits_jobs_prob_for_transition/'
        # The list of items
        files = os.listdir(path)
        files_commit=[os.path.join('./commits_jobs_prob_for_transition/',f) for f in files if str(self.prob_commit) in str(f)]
        # if len(files_commit) == 0:
        #     return 'empty'
        print(files_commit)
        problem_type_list=[]
        if (self.build_prob == 'errored'):
            for f in files_commit:
                # if 'error' in str(f):
                analysis_results = error_classifier.Log_failure_classifier(f).process_file_with_regexes()
                error_types = analysis_results[0]
                print(analysis_results)
                # print(error_types.split(','))
                if error_types.split(',')[1] == 'True':
                    problem_type_list.append('FailMarkedAsError')
                elif error_types.split(',')[2] == 'True':
                    problem_type_list.append('ScriptError')
                elif error_types.split(',')[3] == 'True':
                    problem_type_list.append('BuildDependencyError')
                elif error_types.split(',')[4] == 'True':
                    problem_type_list.append('TravisError')

        elif (self.build_prob == 'failed'):
            for f in files_commit:
                if 'fail' in str(f) :
                    analysis_results = failure_classifier.Log_failure_classifier(f).process_file_with_regexes()
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
        Notes=''
        print('processed commit ' + str(self.prob_commit))
        frequency = collections.Counter(problem_type_list)
        problem_type_main='Undetected'
        try:
            MaxKey = max(frequency, key=frequency.get)
            problem_type_main = MaxKey
        except:
            pass
        if len(problem_type_list) == 0 and self.build_prob == '' and self.build_prob != 'unknown_problem':
            problem_type_main = 'Undetected'
        elif len(problem_type_list) == 0 and problem_type_main == '':
            problem_type_main = 'Unknown'
        return (
        self.git_uri, self.prob_commit, self.fix_commit, problem_type_main, problem_type_list, self.build_prob,
        Notes)

    def find_commit_fail_type(self):
        print('searching for commit '+str(self.prob_commit))
        a=self.find_commit_fil_type_local()
        if a != 'empty':
            return a
        project_git_uri=self.git_uri
        project_name='/'.join(str(project_git_uri).split('/')[3:]).replace('.git','')
        # git_repo=git.repo.Repo(row['ProjectGitRepo'])
        fail_err_commit=str(self.prob_commit)
        fix_commit=str(self.fix_commit)
        # print('searching for commit:'+str(fail_err_commit))
        if(type=='Applied'):
            builds_status_path='../../Project Stats Year/Applied/'+project_name.replace('/','_')+'/build_detailed_info.csv'
        else:
            builds_status_path = '../../Project Stats Year/Tool/' + project_name.replace('/','_') + '/build_detailed_info.csv'
        problem_type_main = ''
        problem_type_list = []
        problem_build_state='unknown_problem'
        Notes=''
        try:
            builds=pd.read_csv(builds_status_path)
            for indexa,rowa in builds.iterrows():
                build_id=rowa['BuildID']
                build_state=rowa['BuildState']
                if build_state == "passed" or build_state == 'canceled':
                    continue
                travis_build=Travis_Utils.get_travis_build(build_id)
                commit_sha=travis_build.commit.sha
                # print('commit found:' + str(commit_sha))
                if commit_sha==fail_err_commit:
                    list_of_jobs=travis_build.jobs
                    if(travis_build.state == 'errored'):
                        problem_build_state = 'errored'
                        for job in list_of_jobs:
                            job = job.get_complete()
                            if job.state =='errored':
                                job_id=job.id
                                if (type == 'Applied'):
                                    log_path='../../Project Stats Year/Applied/'+project_name.replace('/','_')+'/job_logs/'+str(job_id)+'.txt'
                                else:
                                    log_path = '../../Project Stats Year/Tool/' + project_name.replace('/','_') + '/job_logs/' + str(job_id) + '.txt'
                                analysis_results=error_classifier.Log_failure_classifier(log_path).process_file_with_regexes()
                                error_types=analysis_results[0]
                                print(analysis_results)
                                # print(error_types.split(','))
                                if error_types.split(',')[1]=='True':

                                    problem_type_list.append('FailMarkedAsError')
                                elif error_types.split(',')[2]=='True':
                                    problem_type_list.append('ScriptError')

                                elif error_types.split(',')[3]=='True':
                                    problem_type_list.append('BuildDependencyError')

                                elif error_types.split(',')[4] == 'True':
                                    problem_type_list.append('TravisError')

                    elif(travis_build.state == 'failed'):
                        problem_build_state = 'failed'
                        for job in list_of_jobs:
                            job=job.get_complete()
                            if job.state =='failed':
                                job_id=job.id
                                if (type == 'Applied'):
                                    log_path='../../Project Stats Year/Applied/'+project_name.replace('/','_')+'/job_logs/'+str(job_id)+'.txt'
                                else:
                                    log_path = '../../Project Stats Year/Tool/' + project_name.replace('/','_') + '/job_logs/' + str(job_id) + '.txt'
                                analysis_results=failure_classifier.Log_failure_classifier(log_path).process_file_with_regexes()
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

                    print('processed commit '+str(commit_sha))
                    break
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
        if len(problem_type_list) != 0:
            frequency = collections.Counter(problem_type_list)
            try:
                MaxKey = max(frequency, key=frequency.get)
                problem_type_main = MaxKey
            except:
                pass
            return (
            self.git_uri, self.prob_commit, self.fix_commit, problem_type_main, problem_type_list, problem_build_state,Notes)

        try:
            print('commit not found locally, searching travis for commit: '+self.prob_commit)
            travis_repo=Travis_Utils.get_travis_repo(project_name)
            params = {'sort_by': 'started_at:desc'}
            build_page = travis_repo.get_builds(params=params)
            bool_build_next_page = True
            build_found =False
            while bool_build_next_page and (not build_found):
                bool_build_next_page = build_page.has_next_page()
                for build in build_page.builds:
                    if build.is_failed(sync=True) or build.is_errored(sync=True):
                        if str(build.commit.sha) == str(self.prob_commit):
                            print('found commit ' + str(self.prob_commit))
                            if build.is_failed(sync=True):
                                problem_build_state='failed'
                            else:
                                problem_build_state = 'errored'
                            job_page = build.get_jobs()
                            bool_job_next_page = True
                            while (bool_job_next_page):
                                bool_job_next_page = job_page.has_next_page()
                                for job in job_page.jobs:
                                    if (job.is_failed(sync=True) and build.is_failed(sync=True)):
                                        try:
                                            output_str = job.get_log().content
                                        except Exception:
                                            problem_type_list.append('log not found')
                                            continue
                                        if (output_str == "" or output_str is None):
                                            problem_type_list.append('log empty')
                                        else:
                                            with open('commits_jobs_prob_for_transition\\fail_' + str(job.id) + '_' + str(
                                                    self.prob_commit) + '.txt', 'w+',encoding='utf-8') as file:
                                                file.write(output_str)
                                                print(output_str[:10])
                                                file.flush()
                                            analysis_results = failure_classifier.Log_failure_classifier(
                                                'commits_jobs_prob_for_transition\\fail_' + str(job.id) + '_' + str(
                                                    self.prob_commit) + '.txt').process_file_with_regexes()
                                            fail_types = analysis_results[0]
                                            print(fail_types.split(','))
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
                                    if (job.is_errored(sync=True) and build.is_errored()):
                                        try:
                                            output_str = job.get_log().content
                                        except Exception:
                                            problem_type_list.append('log not found')
                                            continue
                                        if (output_str == "" or output_str is None):
                                            problem_type_list.append('log empty')
                                            continue
                                        else:
                                            with open('commits_jobs_prob_for_transition\\error_'+str(job.id)+'_'+str(self.prob_commit)+'.txt', 'w+',
                                                      encoding='utf-8') as file:
                                                file.write(output_str)
                                                print(output_str[:10])
                                                file.flush()
                                            analysis_results = error_classifier.Log_failure_classifier(
                                                'commits_jobs_prob_for_transition\\error_' + str(job.id) + '_' + str(
                                                    self.prob_commit) + '.txt').process_file_with_regexes()
                                            error_types = analysis_results[0]
                                            print(analysis_results)
                                            if error_types.split(',')[1] == 'True':

                                                problem_type_list.append('FailMarkedAsError')
                                            elif error_types.split(',')[2] == 'True':
                                                problem_type_list.append('ScriptError')

                                            elif error_types.split(',')[3] == 'True':
                                                problem_type_list.append('BuildDependencyError')

                                            elif error_types.split(',')[4] == 'True':
                                                problem_type_list.append('TravisError')

                                if bool_job_next_page:
                                    job_page = job_page.next_page()
                            build_found=True
                            break
                if bool_build_next_page:
                    build_page = build_page.next_page()

            # if build_found == False:
            #     git_repo=git.Repo(project_name)
            #     parent=git_repo.commit(self.prob_commit).commit.parents[0]
            #     print('commit '+self.prob_commit+' not found, searching travis for its parent commit: ' + parent)
            #     params = {'sort_by': 'started_at:desc'}
            #     build_page = travis_repo.get_builds(params=params)
            #     bool_build_next_page = Truesk
            #     build_found = False
            #     while bool_build_next_page and (not build_found):
            #         bool_build_next_page = build_page.has_next_page()
            #         for build in build_page.builds:
            #             if build.is_failed(sync=True) or build.is_errored(sync=True):
            #                 if str(build.commit.sha) == str(parent):
            #                     print('found parent commit ' + str(parent))
            #                     Notes='ProbCommitNotFound,UsingParent: '+str(parent)
            #                     if build.is_failed(sync=True):
            #                         problem_build_state = 'failed'
            #                     else:
            #                         problem_build_state = 'errored'
            #                     job_page = build.get_jobs()
            #                     bool_job_next_page = True
            #                     while (bool_job_next_page):
            #                         bool_job_next_page = job_page.has_next_page()
            #                         for job in job_page.jobs:
            #                             if (job.is_failed(sync=True) and build.is_failed(sync=True)):
            #                                 try:
            #                                     output_str = job.get_log().content
            #                                 except Exception:
            #                                     continue
            #                                 if (output_str == "" or output_str is None):
            #                                     continue
            #                                 else:
            #                                     with open('temp.txt', 'w+', encoding='utf-8') as file:
            #                                         file.write(output_str)
            #                                         print(output_str[:10])
            #                                         file.flush()
            #                                     analysis_results = failure_classifier.Log_failure_classifier(
            #                                         'temp.txt').process_file_with_regexes()
            #                                     fail_types = analysis_results[0]
            #                                     print(fail_types.split(','))
            #                                     if fail_types.split(',')[1] == 'True':
            #                                         problem_type_list.append('TestFail')
            #
            #                                     elif fail_types.split(',')[2] == 'True':
            #                                         problem_type_list.append('BuildError')
            #
            #                                     elif fail_types.split(',')[3] == 'True':
            #                                         problem_type_list.append('TestError')
            #
            #                                     elif fail_types.split(',')[4] == 'True':
            #                                         problem_type_list.append('CodeAnalysisError')
            #
            #                                     elif fail_types.split(',')[5] == 'True':
            #                                         problem_type_list.append('TravisFail')
            #
            #                                     elif fail_types.split(',')[6] == 'True':
            #                                         problem_type_list.append('DeploymentError')
            #
            #                             if (job.is_errored(sync=True) and build.is_errored()):
            #                                 output_str = job.get_log().content
            #                                 if (output_str == "" or output_str == None):
            #                                     continue
            #                                 else:
            #                                     try:
            #                                         output_str = job.get_log().content
            #                                     except Exception:
            #                                         continue
            #                                     if (output_str == "" or output_str is None):
            #                                         continue
            #                                     else:
            #                                         with open('temp.txt', 'w+',
            #                                                   encoding='utf-8') as file:
            #                                             file.write(output_str)
            #                                             print(output_str[:10])
            #                                             file.flush()
            #                                         analysis_results = error_classifier.Log_failure_classifier(
            #                                             'temp.txt').process_file_with_regexes()
            #                                         error_types = analysis_results[0]
            #                                         print(analysis_results)
            #                                         if error_types.split(',')[1] == 'True':
            #                                             problem_type_list.append('FailMarkedAsError')
            #                                         elif error_types.split(',')[2] == 'True':
            #                                             problem_type_list.append('ScriptError')
            #
            #                                         elif error_types.split(',')[2] == 'True':
            #                                             problem_type_list.append('BuildDependencyError')
            #
            #                                         elif error_types.split(',')[3] == 'True':
            #                                             problem_type_list.append('TravisError')
            #
            #                         if bool_job_next_page:
            #                             job_page = job_page.next_page()
            #                     build_found = True
            #                     break
            #         if bool_build_next_page:
            #             build_page = build_page.next_page()
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
        print('processed commit: '+self.prob_commit)
        frequency = collections.Counter(problem_type_list)
        try:
            MaxKey = max(frequency, key=frequency.get)
            problem_type_main = MaxKey
        except:
            pass
        if len(problem_type_list)==0 and problem_type_main =='' and problem_build_state!='unknown_problem':
            problem_type_main='Undetected'
        elif len(problem_type_list)==0 and problem_type_main =='':
            problem_type_main='Unknown'
        return(self.git_uri,self.prob_commit,self.fix_commit,problem_type_main,problem_type_list,problem_build_state,Notes)


NUM_CORE = 8

def worker(arg):
    obj= arg
    return obj.find_commit_fail_type()

if __name__ == "__main__":
    start_time_all = time.perf_counter()
    applied=pd.read_csv('Applied_transition_with_problem.csv')
    tool=pd.read_csv('Tool_transition_with_problem.csv')
    applied=applied.loc[applied['MainProblem']=='Unknown']
    tool.fillna('0')
    # pprint(tool.columns)
    tool=tool.loc[tool['MainProblem']=='Unknown'] #[commit_failure_classifier(row['ProjectGitRepo'],row['Failed-ErrorredCommitID'],row['FixCommitID'],'Tool') for index,row in applied.iterrows()]+
    # pprint(tool['MainProblem'].to_list())
    # exit()
    list_of_objects = [commit_failure_classifier(row['ProjectGitRepo'],row['Failed-ErrorredCommitID'],row['FixCommitID'],row['ProblemBuildState'],'Tool') for index,row in tool.iterrows()]
    pool = mp.Pool(NUM_CORE)
    list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()
    csv_res = open('../../CSV Outputs/build_problem_commits_error_unknown_fix_tool.csv', 'w+')
    csv_res.write(
        'ProjectGitRepo,Failed-ErrorredCommitID,FixCommitID,MainProblem,AllProblems,ProblemBuildState')
    csv_res.write('\n')
    for res in list_of_results:
        csv_res.write(res[0]+','+str(res[1])+','+str(res[2])+','+str(res[3])+','+str(res[4])+','+str(res[5])+','+str(res[6]))
        csv_res.write('\n')
    # list_of_objects = [
    #     commit_failure_classifier(row['ProjectGitRepo'], row['Failed-ErrorredCommitID'], row['FixCommitID'],
    #                               row['ProblemBuildState'], 'Applied') for index, row in applied.iterrows()]
    # pool = mp.Pool(NUM_CORE)
    # list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    # pool.close()
    # pool.join()
    # csv_res = open('../../CSV Outputs/build_problem_commits_error_redo_applied.csv', 'w+')
    # csv_res.write(
    #     'ProjectGitRepo,Failed-ErrorredCommitID,FixCommitID,MainProblem,AllProblems,ProblemBuildState')
    # csv_res.write('\n')
    # for res in list_of_results:
    #     csv_res.write(
    #         res[0] + ',' + str(res[1]) + ',' + str(res[2]) + ',' + str(res[3]) + ',' + str(res[4]) + ',' + str(
    #             res[5]) + ',' + str(res[6]))
    #     csv_res.write('\n')

    # a=commit_failure_classifier('git://github.com/kakaobrain/torchgpipe.git','b3ae91c7e89644a73b9e9e44391d034bf746342f','4913a915adfd7f4b8fde66c3edfe01aebb929fb7').find_commit_fail_type()
    # print(a)
