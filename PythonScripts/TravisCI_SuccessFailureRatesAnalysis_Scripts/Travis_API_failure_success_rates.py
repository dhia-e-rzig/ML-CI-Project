import datetime

import pandas as pd
from PythonScripts.Utils import Travis_Utils
df=pd.read_csv('../../CSV Inputs/python_projects_with_travis_info.csv')


List_of_tool_repos=df.loc[df['RepoType']=='Tool']['RepoName'].to_list()
List_of_applied_repos=df.loc[df['RepoType']=='Applied']['RepoName'].to_list()


class Project_State_Processor_class():
    def __init__(self, project,type):
        self.project = project
        self.type = type
        self.result = ""

    def find_project_rates_between_dates(self, date_beg, date_end):
        start_time_all = time.perf_counter()
        project=self.project
        project_csv = open('Project Stats Year/'+str(self.type)+'/' + project.replace('/', '_') + '.csv', 'w+')
        project_csv.write('BuildID,BuildCreationDate,BuildState,BuildDuration')
        project_csv.write('\n')
        try:
            travis_repo = Travis_Utils.get_travis_repo(project)
        except:
            project_csv.write('ProjectNotFound')
            project_csv.write('\n')
            return
        params = {'sort_by': 'started_at:desc'}

        try:
            build_page = travis_repo.get_builds(params=params)
            if(build_page is None ) or build_page.builds is None:
                return
            bool_build_next_page = True
            while (bool_build_next_page):
                bool_build_next_page = build_page.has_next_page()
                if build_page is None or build_page.builds is None:
                    return
                oldest_build_on_page = build_page.builds[-1]
                i = len(build_page.builds) - 2
                while (oldest_build_on_page.started_at is None and i > -1):
                    oldest_build_on_page = build_page.builds[i]
                    i = i - 1
                if (i == -1):
                    return
                if (oldest_build_on_page.started_at.date() > date_end and  build_page.has_next_page()):
                        build_page = build_page.next_page()
                        bool_build_next_page = build_page.has_next_page()
                        continue
                if build_page is None or build_page.builds is None:
                    return
                newest_build_on_page = build_page.builds[0]
                i = 1
                while (newest_build_on_page.started_at is None and i < len(build_page.builds)):
                    newest_build_on_page = build_page.builds[i]
                    i = i+1
                if (i == len(build_page.builds)):
                    return
                if (newest_build_on_page.started_at.date() < date_beg):
                        return
                for build in build_page.builds:
                    try:
                        if(build.started_at is None):
                            continue
                        if(build.started_at.date()> date_end):
                            continue
                        if(build.started_at.date()<date_beg):
                            return
                        print(str(project)+','+str(build.id) + ',' + str(build.started_at.date()) + ',' + str(build.state) + ',' + str(build.duration))
                        project_csv.write(
                            str(build.id) + ',' + str(build.started_at.date()) + ',' + str(build.state) + ',' + str(build.duration))
                        project_csv.write('\n')
                    except Exception as e:
                        with open("travis_api_succes_rates_err.txt", "a+") as error:
                            error.write(project +'buildID'+str(build.id)+' ' + str(e))
                            error.write('\n')
                            print(project +'buildID'+str(build.id)+' ' + str(e))
                if bool_build_next_page:
                    if build_page.next_page() is None:
                        return
                    build_page = build_page.next_page()
        except Exception as e:
            with open("travis_api_succes_rates_err.txt","a+") as error:
                error.write(project+' '+str(e))
                error.write('\n')
                print(project+' '+str(e))

        end_time_all = time.perf_counter()
        print("Execution Time for "+project+f" : {end_time_all - start_time_all:0.6f}")
import multiprocessing as mp
NUM_CORE = 8
import time

def worker(arg):
    obj, date_beg,date_end= arg
    return obj.find_project_rates_between_dates(date_beg,date_end)

if __name__ == "__main__":
    start_time_all = time.perf_counter()
    # log_files = os.listdir('FailedLogs-ForTesting')
    list_of_objects = [Project_State_Processor_class(i,'Applied') for i in List_of_applied_repos] +[Project_State_Processor_class(i,'Tool') for i in List_of_tool_repos]
    pool = mp.Pool(NUM_CORE)
    date_beg=datetime.date(2020, 5, 13)
    date_end=datetime.date(2021, 5, 13)
    list_of_results = pool.map(worker, ((obj,date_beg,date_end) for obj in list_of_objects))
    pool.close()
    pool.join()
    end_time_all = time.perf_counter()
    print(f"Execution Time for all : {end_time_all - start_time_all:0.6f}")
