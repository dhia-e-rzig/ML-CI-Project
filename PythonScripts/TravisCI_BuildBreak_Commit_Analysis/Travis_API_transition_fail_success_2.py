import datetime
import time

import pandas as pd
from pydriller import Repository, Git
from github import Github
from PythonScripts.Utils import Github_Utils

df=pd.read_csv('repeat_stats.csv')
import os
import sys
# List_of_tool_repos=df.loc[(df['RepoType']=='Tool') & (df['ML-AI']=='Yes') ]['RepoName'].to_list()
# List_of_applied_repos=df.loc[(df['RepoType']=='Applied') & (df['ML-AI']=='Yes')]['RepoName'].to_list()

g=Github(Github_Utils.get_github_token())

class Project_State_Processor_class():
    def __init__(self, project,type,output_file):
        self.project = project
        self.type = type
        self.output_file=output_file
        self.result = ""

    def find_build_transition(self):
        project=self.project
        # script_path = os.path.realpath(__file__)
        script_path='../../Projects Stats Build Transition'
        project_folder_path = os.path.join(script_path, str(self.type)+'/' + project.replace('/', '_'))
        project_csv_build = open(project_folder_path+'/' + 'build_transition.csv', 'r+')
        print(project+' processing')
        try:
            df=pd.read_csv(project_csv_build)
            if (df['BuildID'].to_list()[0] == 'ProjectNotFound'):
                return
            commit_list=df['CommitID'].to_list()
            commits_to_process = len(commit_list)
            commits_processed=0 #commits processed
            while commits_processed<commits_to_process:
                try:
                    gh_repo=g.get_repo(project)
                    url=gh_repo.git_url
                    x=commits_processed
                    for i in range(x,commits_to_process-1,2):
                        commit_1_ID=commit_list[i]
                        commit_2_ID=commit_list[i+1]
                        commit_2_pull_nb= str(df.loc[df['CommitID'] == commit_2_ID]['ComparisonURL'].to_list()[0]).split('/')[-1]
                        State_2 = df.loc[df['CommitID'] == commit_2_ID]['BuildState'].to_list()[0]
                        Pull=False
                        if State_2 == 'passed':
                            try:
                                commit_object=gh_repo.get_commit(commit_2_ID)
                                files = commit_object.files
                            except:
                                Pull=True
                                pull_commits=gh_repo.get_pull(int(commit_2_pull_nb)).get_commits()
                                commit_obj=pull_commits[0]
                                files= commit_obj.files
                            TravisFileFound=False
                            for file in files:
                                if str(file.filename).endswith('travis.yml'):
                                    TravisFileFound=True
                                    break
                            if TravisFileFound:
                                # State_1=df.loc[df['CommitID']==commit_1_ID]['BuildState']
                                    if not Pull:
                                        print((str(url+','+commit_1_ID+','+commit_2_ID+',N/A')))
                                        self.output_file.write(str(url+','+commit_1_ID+','+commit_2_ID+',N/A'))
                                        self.output_file.write('\n')
                                    else:
                                        print((str(url + ',' + commit_1_ID + ',' + commit_2_ID+','+commit_2_pull_nb)))
                                        self.output_file.write(str(url + ',' + commit_1_ID + ',' + commit_2_ID+','+commit_2_pull_nb))
                                        self.output_file.write('\n')

                        commits_processed+=2
                        print(str(commits_processed)+' out of '+str(commits_to_process))
                except Exception as e:
                    self.output_file.flush()
                    print('Exception')
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    # Github_Utils.is_over_core_rate(g)
                    if Github_Utils.is_over_core_rate(g):
                        Github_Utils.sleep_until_core_rate_reset(g)
                    else:
                        commits_processed+=2
        except Exception as e:
            self.output_file.flush()
            print('Exception')
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

start_time_all = time.perf_counter()
# output_applied=open('Applied_transition.csv','a+',encoding='utf-8')
# output_applied.write('ProjectGitRepo,Failed-ErrorredCommitID,FixCommitID')
# output_applied.write('\n')
# output_applied.flush()
output_tool=open('Tool_transition.csv','a+',encoding='utf-8')
output_tool.write('ProjectGitRepo,Failed-ErrorredCommitID,FixCommitID,FixCommitPullNb')
output_tool.write('\n')
output_tool.flush()
# [Project_State_Processor_class(i,'Applied',output_applied) for i in List_of_applied_repos] +
list_of_objects = [Project_State_Processor_class(i,'Tool',output_tool) for i in List_of_tool_repos]

project_found=True
for class_el in list_of_objects:
    # if(class_el=='project'):
    #     project_found=True
    # if(not project_found):
    #     continue
    class_el.find_build_transition()

end_time_all = time.perf_counter()
print(f"Execution Time for all : {end_time_all - start_time_all:0.6f}")
