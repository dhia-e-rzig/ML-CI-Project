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
from datetime import  date, timedelta

nonml_travis_projects_df=pd.read_csv('../../CSV Input - New/RQ3_4_NonML.csv')
ml_travis_projects_df=pd.read_csv('../../CSV Input - New/RQ3-RQ4-new.csv')
cutoff_list = [date(2021,8,12)] #,date(2020, 8, 12), date(2019, 8, 12), date(2018, 8, 12)]

class travis_repo_finder():
    def __init__(self, full_name,category):
        self.full_name = full_name
        self.category=category
    def find_travis(self):
        print('processing '+self.full_name)
        return_dict= {}
        # if (self.full_name == "tdryer/hangups"):
        #     travis_repo = get_travis_repo(self.full_name, verboseMode=False)
        #     build_page = travis_repo.get_builds()
        for cutoff in cutoff_list:
            job_fail_count=0
            job_error_count=0
            notFinishedBecauseOfTravisCIError=True
            # while(notFinishedBecauseOfTravisCIError):
            try:
                travis_repo=get_travis_repo(self.full_name,verboseMode=False)
                # if(travis_repo == None):
                #     print('travis repo not found')
                #     return_dict[
                #         cutoff] = self.full_name + ',' + self.category + ',' + "NoneFound" + ',' + "NoneFound" + ',' + "NoneFound" + ',' + "0,0," + "0" + ',' + "0"
                #     continue
                build_page = travis_repo.get_builds()
                if (build_page is None) or build_page.builds is None:
                    continue
                bool_build_next_page = build_page.has_next_page()
                if build_page is None or build_page.builds is None:
                    continue
                last_build = build_page.builds[0]
                while last_build.started_at is None or last_build.started_at.date() > cutoff:
                    i =len(build_page.builds) - 1
                    while (i > -1 ) and (last_build.started_at is None or last_build.started_at.date() > cutoff):
                        last_build = build_page.builds[i]
                        i = i - 1
                    bool_build_next_page = build_page.has_next_page()
                    if bool_build_next_page and (last_build.started_at is None or last_build.started_at.date() > cutoff):
                        build_page = build_page.next_page()
                    elif (not bool_build_next_page) and (last_build.started_at is None or last_build.started_at.date() > cutoff):
                        break

                if(last_build.started_at is None or last_build.started_at.date() > cutoff):
                    print('oldest before cutoff not found '+self.full_name)
                    return_dict[
                        cutoff] =  self.full_name + ',' + self.category + ',' + "NoneFound" + ',' + "NoneFound" + ',' + "NoneFound" + ',' + "0,0,"+"0"
                    continue

                date_end = last_build.started_at.date() + timedelta(days=1)
                date_beg = date_end - timedelta(days=366)
                while (bool_build_next_page):
                    bool_build_next_page = build_page.has_next_page()
                    if build_page is None or build_page.builds is None:
                        break
                    oldest_build_on_page = build_page.builds[-1]

                    i = len(build_page.builds) - 1
                    while (oldest_build_on_page.started_at is None and i > -1):
                        oldest_build_on_page = build_page.builds[i]
                        i = i - 1

                    if (oldest_build_on_page.started_at is None and build_page.has_next_page()):
                        build_page = build_page.next_page()
                        bool_build_next_page = build_page.has_next_page()
                        continue
                    if (oldest_build_on_page.started_at.date() > date_end and build_page.has_next_page()):
                        build_page = build_page.next_page()
                        bool_build_next_page = build_page.has_next_page()
                        continue
                    if build_page is None or build_page.builds is None:
                        break
                    newest_build_on_page = build_page.builds[0]
                    i = 1
                    while (newest_build_on_page.started_at is None and i < len(build_page.builds)):
                        newest_build_on_page = build_page.builds[i]
                        i = i + 1
                    if (i == len(build_page.builds)):
                        break
                    if (newest_build_on_page.started_at.date() < date_beg):
                        break
                    if build_page is None or build_page.builds is None:
                        break

                    for build in build_page.builds:
                        # print(self.full_name+'--buildid--'+build.id.__str__())
                        try:
                            if (build.started_at is None):
                                continue
                            if (build.started_at.date() > date_end):
                                continue
                            if (build.started_at.date() < date_beg):
                                break
                            if build.is_failed(sync=True) or build.is_errored(sync=True):
                                job_page = build.get_jobs()
                                bool_job_next_page = True
                                while (bool_job_next_page):
                                    bool_job_next_page = job_page.has_next_page()
                                    for job in job_page.jobs:
                                        if (job.is_failed()):
                                            job_fail_count+=1
                                        elif (job.is_errored()):
                                            job_error_count+=1
                                    if bool_job_next_page:
                                        job_page = job_page.next_page()
                            else:
                                continue
                        except Exception as e:
                            raise e
                    if build_page is None:
                        break
                    if build_page.has_next_page() is None or build_page.has_next_page() is False:
                        break
                    try:
                        # print(build_page.has_next_page())
                        build_page = build_page.next_page()
                    except Exception as e:
                        with open("travis_investigator.txt", "a+") as error:
                            error.write(self.full_name+'--'+self.category + ',buildID' + '00' + ',' + str(e))
                            error.write('\n')
                            print(self.full_name+'--'+self.category + 'buildID' + '00' + ' ' + str(e))
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            print(exc_type, fname, exc_tb.tb_lineno)
                        break
                first_page=travis_repo.get_builds().builds
                last_build = first_page[0]
                i=0
                # print(last_build.started_at)
                while last_build.started_at is None:
                    last_build = first_page[i]
                    i+=1
                last_page=travis_repo.get_builds().last_page().builds
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
                return_dict[cutoff] = self.full_name + ',' + self.category + ',' + date_beg.__str__() + ',' + date_end.__str__() + ',' + str(total_run_count) + ',' + str(days)+','+str(job_fail_count)+','+str(job_error_count)
                notFinishedBecauseOfTravisCIError=False
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                # else:
                #     if job_fail_count == 0 and job_error_count == 0:
                #         return_dict[
                #             cutoff] = self.full_name + ',' + self.category + ',' + "NoneFound" + ',' + "NoneFound" + ',' + "NoneFound" + ',' + "0,0," + "0"
                #     notFinishedBecauseOfTravisCIError=False
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print('EXCEPTION: ' + self.full_name)
                print(e)
                print(exc_type, fname, exc_tb.tb_lineno)
                return_dict_2={}
                return_dict_2['repeat'] = True
                return_dict_2['name'] = self.full_name
                return_dict_2['category'] = self.category
                return return_dict_2
        return return_dict


NUM_CORE = mp.cpu_count()

def worker_1(arg):
    obj= arg
    return obj.find_travis()


if __name__ == "__main__":
    start_time_all = time.perf_counter()
    # # # print('start time for nonml'+start_time_all.__str__())
    # # # applied=pd.read_csv('Applied_transition_with_problem.csv')
    # print('starting NonML')
    # list_of_objects = [travis_repo_finder(row['RepoName'],row['RepoType']) for index,row in nonml_travis_projects_df.iterrows()]
    # pool = mp.Pool(NUM_CORE)
    # list_of_results = pool.map(worker_1, ((obj) for obj in list_of_objects))
    # pool.close()
    # pool.join()
    # repeat_list=[]
    # for cutoff in cutoff_list:
    #     f_travis_history_stats = open('Travisci_history_stats_nonml_investig_1year_'+cutoff.__str__()+'.csv', 'w+')
    #     f_travis_history_stats.write('ProjectName,ProjectType,StartDate,EndDate,TotalRuns,DaysOfCIActivity,JobFailCount,JobErrorCount\n')
    #     for res in list_of_results:
    #         if cutoff in list(res.keys()):
    #             str_out = res[cutoff]
    #             f_travis_history_stats.write(str_out + '\n')
    #         else:
    #                 repeat_list.append((res['name'], res['category']))
    #                 continue
    #
    # # end_time_all = time.perf_counter()
    #
    # list_of_objects = [travis_repo_finder(x[0], x[1]) for x in repeat_list]
    # pool = mp.Pool(2)
    # list_of_results = pool.map(worker_1, ((obj) for obj in list_of_objects))
    # pool.close()
    # pool.join()
    # repeat_list = []
    # for cutoff in cutoff_list:
    #     f_travis_history_stats = open('Travisci_history_stats_nonml_investig_1year_' + cutoff.__str__() + '.csv', 'a+')
    #     # f_travis_history_stats.write(
    #     #     'ProjectName,ProjectType,StartDate,EndDate,TotalRuns,DaysOfCIActivity,JobFailCount,JobErrorCount\n')
    #     for res in list_of_results:
    #         if cutoff in list(res.keys()):
    #             str_out = res[cutoff]
    #             f_travis_history_stats.write(str_out + '\n')
    #         else:
    #             print('error')
    #             print(res['name']+'--'+res['category'])
    # end_time_all = time.perf_counter()
    # print(f"Execution Time for nonml : {end_time_all - start_time_all:0.6f}")
    # ML
    print('starting ML')
    list_of_objects = [travis_repo_finder(row['RepoName'], row['RepoType']) for index, row in
                       ml_travis_projects_df.iterrows()]
    pool = mp.Pool(NUM_CORE)
    list_of_results = pool.map(worker_1, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()
    repeat_list = []
    for cutoff in cutoff_list:
        f_travis_history_stats = open('Travisci_history_stats_ml_investig_1year_' + cutoff.__str__() + '.csv', 'w+')
        f_travis_history_stats.write(
            'ProjectName,ProjectType,StartDate,EndDate,TotalRuns,DaysOfCIActivity,JobFailCount,JobErrorCount\n')
        for res in list_of_results:
            if cutoff in list(res.keys()):
                str_out = res[cutoff]
                f_travis_history_stats.write(str_out + '\n')
            else:
                repeat_list.append((res['name'], res['category']))
                continue

    # end_time_all = time.perf_counter()
    print('running repeat')
    list_of_objects = [travis_repo_finder(x[0], x[1]) for x in repeat_list]
    pool = mp.Pool(2)
    list_of_results = pool.map(worker_1, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()
    repeat_list = []
    for cutoff in cutoff_list:
        f_travis_history_stats = open('Travisci_history_stats_ml_investig_1year_' + cutoff.__str__() + '.csv', 'a+')
        # f_travis_history_stats.write(
        #     'ProjectName,ProjectType,StartDate,EndDate,TotalRuns,DaysOfCIActivity,JobFailCount,JobErrorCount\n')
        for res in list_of_results:
            if cutoff in list(res.keys()):
                str_out = res[cutoff]
                f_travis_history_stats.write(str_out + '\n')
            else:
                print('error')
                print(res['name'] + '--' + res['category'])
    end_time_all = time.perf_counter()
    print(f"Execution Time for nonml : {end_time_all - start_time_all:0.6f}")