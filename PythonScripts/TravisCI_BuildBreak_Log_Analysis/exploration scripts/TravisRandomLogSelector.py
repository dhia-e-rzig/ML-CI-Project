import os
from pprint import pprint

import pandas as pd
import random
import shutil


df=pd.read_csv('../../CSV Inputs/python_projects_with_travis_info_curated.csv')
List_of_tool_repos=df.loc[ (df['RepoType']=='Tool') & (df['ML-AI']=='Yes')]['RepoName'].to_list()
List_of_applied_repos=df.loc[(df['RepoType']=='Applied') & (df['ML-AI']=='Yes') ]['RepoName'].to_list()
df_devops_class=pd.read_csv('../../CSV Inputs/devops project type/All_projects_classification.csv')


# List_of_tool_withDeploy=[ x for x in List_of_tool_repos if df_devops_class[df_devops_class['ProjectName']==x]['DeploymentAutomation'].tolist()[0] == 1 ]
# pprint(List_of_tool_withDeploy)
# List_of_applied_withDeploy=[ x for x in List_of_applied_repos if df_devops_class[df_devops_class['ProjectName']==x]['DeploymentAutomation'].tolist()[0] == 1 ]
# pprint(List_of_applied_withDeploy)

all_pd=pd.DataFrame(columns=["JobID","JobCreationDate","JobState","JobFinishedAt","JobDuration","Path"])

for project in List_of_applied_repos:
    try:
        project_csv = pd.read_csv('../../Project Stats Year/' + "Applied" + '/' + project.replace('/','_') + '/job_detailed_info.csv',encoding='utf-8')
        project_csv['Path']=str('../../Project Stats Year/' + "Applied" + '/' + project.replace('/','_') + '/job_logs/')
        all_pd=pd.concat([all_pd,project_csv],axis=0)
    except Exception as e :
        print(str(e))
        continue


all_pd_failed_list=all_pd.loc[all_pd['JobState']=='failed']
all_pd_errored_list=all_pd.loc[all_pd['JobState']=='errored']

number= 15
# random_failed_list = all_pd_failed_list.sample(n=number)
random_errored_list = all_pd_errored_list.sample(n=number)


# random_failed_list=random_failed_list.loc[random_failed_list.apply(lambda x: True if os.path.getsize(str(x['Path']) + str(x['JobID']) + '.txt') > 15 else False, axis=1)]
random_errored_list=random_errored_list.loc[random_errored_list.apply(lambda x: True if os.path.getsize(str(x['Path']) + str(x['JobID']) + '.txt') > 15 else False, axis=1)]

# while random_failed_list.shape[0]<number:
#     random_failed_list_2 = all_pd_failed_list.sample(n=number - random_failed_list.shape[0])
#     random_failed_list=pd.concat([random_failed_list,random_failed_list_2],axis=0)
#     random_failed_list.drop_duplicates(inplace=True)
#
# for index, row in random_failed_list.iterrows():
#     target = "../../FailedLogs-ForAccuracyTesting2/"+str(row['JobID'])+'.txt'
#     shutil.copyfile(str(row['Path'])+str(row['JobID'])+'.txt', target)
#
# with open("../../FailedLogs-ForAccuracyTesting2/files_ground_truth2.csv",'w+') as f:
#     f.write("file_name") #,TestFail,BuildError,TestError,CodeAnalysisError,TravisError
#     f.write('\n')
#     for index, row in random_failed_list.iterrows():
#         f.write(str(str(row['JobID'])+'.txt'))#+',,,,,'
#         f.write('\n')


while random_errored_list.shape[0]<number:
    random_errored_list_2 = all_pd_failed_list.sample(n=number - random_errored_list.shape[0])
    random_errored_list=pd.concat([random_errored_list,random_errored_list_2],axis=0)
    random_errored_list.drop_duplicates(inplace=True)

for index, row in random_errored_list.iterrows():
    target = "../../ErroredLogs-ForMining/"+str(row['JobID'])+'.txt'
    shutil.copyfile(str(row['Path'])+str(row['JobID'])+'.txt', target)

with open("../../ErroredLogs-ForMining/files_ground_truth2.csv",'w+') as f:
    f.write("file_name") #,TestFail,BuildError,TestError,CodeAnalysisError,TravisError
    f.write('\n')
    for index, row in random_errored_list.iterrows():
        f.write(str(str(row['JobID'])+'.txt'))#+',,,,,'
        f.write('\n')
