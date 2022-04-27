import os
import pandas as pd
from os import path
df_ml=pd.read_csv('../../CSV Input - New/RQ3-RQ4-new.csv')
df_nonml=pd.read_csv('../../CSV Input - New/RQ3_4_NonML.csv')
list_applied=df_ml[df_ml['RepoType']=='Applied']['RepoName'].tolist()
print(list_applied)

list_tool=df_ml[df_ml['RepoType']=='Tool']['RepoName'].tolist()

print(list_tool)
out=open('log-tool-mismatch.txt','w+')
list_nonml=df_nonml['RepoName'].tolist()


list_tool_paths=[str(el).replace('/','_') for el in list_tool]

# for loc_path, folders, files in os.walk('../../Project Stats Year/Tool/'):
#     arr=loc_path.split('/')
#     if arr[4] not in list_tool_paths:
#         print(arr[4])
#
# for project in list_tool:
#     if not path.exists('../../Project Stats Year/Tool/' + str(project).replace('/', '_', 1) + '/job_logs'):
#         print(project+' not found !!')
#         continue
# exit()




for project in list_tool:
    if not path.exists('../../Project Stats Year/Tool/' + str(project).replace('/', '_', 1) + '/job_logs'):
        print(project+' not found !!')
        continue
    logs_count = 0
    # logs_with_str = 0
    if not path.exists('../../Project Stats Year/Tool/' + str(project).replace('/', '_', 1) + '/job_detailed_info.csv'):
        print('job info not found !')
        continue
    else:
        try:
            job_df=pd.read_csv('../../Project Stats Year/Tool/' + str(project).replace('/', '_', 1) + '/job_detailed_info.csv')
            total_failed=len(job_df[job_df['JobState']=='failed']['JobID'].tolist())
            total_errored=len(job_df[job_df['JobState']=='errored']['JobID'].tolist())
            total_prob=total_errored+total_failed
        except:
            print('job csv problem for project'+project)
            out.write('job csv problem for project'+project+'\n')

    for loc_path, folders, files in os.walk('../../Project Stats Year/Tool/'+str(project).replace('/','_',1)+'/job_logs'):
        for file in files:
            if(str(file).endswith('.txt')):
                logs_count+=1
    print(project+'  -total'+str(logs_count)+' -with project'+str(total_prob))
    out.write(project+'  -total'+str(logs_count)+' -with project'+str(total_prob)+'\n')
    if(logs_count != total_prob):
        print('ERROR, logs unequal '+project)
        out.write('ERROR, job logs unequal '+project+'\n')

    if(logs_count == 0) and not path.exists('../../Project Stats Year/Tool/' + str(project).replace('/', '_', 1) + '/dates.csv'):
        print(project + ' empty')
        out.write(project + ' empty\n')


