import pandas as pd
from git import Repo
import datetime
format = "%Y-%m-%d"
import pytz
from os import path

df = pd.read_csv('../CSV Input - New/RQ1_Applied_New.csv', sep=';')
df_2 = pd.read_csv('../CSV Input - New/RQ1_Tool_New.csv', sep=';')
df_3 = pd.read_csv('../CSV Input - New/NonML-classification.csv', sep=';')



# df_ml=df.loc[df['ML-AI']=='Yes']
exceptions= open("exceptions-3.txt", "a+")
paths= open("exceptions-paths-3.csv", "a+")
paths.write('Path\n')
# git pull on repos
for index,row in df.iterrows():
    path1='/media/umd-002677/TOSHIBA EXT/PhD Work/repos/'+'applied'+'/'+row['ProjectName']
    path2='/media/umd-002677/TOSHIBA EXT/PhD Work/repos/'+'tool'+'/'+row['ProjectName']
    if(path.exists(path1)):
        path_temp = path1
    elif(path.exists(path2)):
        path_temp=path2
    else:
        exceptions.write('Paths Not Found: '+row['ProjectName']+'\n')
        continue
    # path='/media/umd-002677/TOSHIBA EXT/PhD Work/repos/no-ai-ml/CameloeAnthony/AndroidArchitectureCollection'
    # path='/media/umd-002677/TOSHIBA EXT/PhD Work/repos/no-ai-ml/12207480/TYCyclePagerView'
    try:
        print(path_temp)
        git_repo=Repo(path_temp)
        a=git_repo.git.pull()
        print(a)
    except Exception as e:
        print(e)
        git_repo = Repo(path_temp)
        try:
            print('retrying')
            print(path)
            git_repo.git.reset('--hard')
            git_repo.git.clean('-fd')
            b=git_repo.git.pull('--allow-unrelated-histories')
            print(b)
        except Exception as e1:
            print(e1)
            try:
                print('retrying again')
                git_repo.git.reset('--hard')
                git_repo.git.clean('-fd')
                git_repo.git.fetch()
                c= git_repo.git.rebase()
                print(c)
            except Exception as e2:
                print(e2)
                try:
                    print('retrying again again')
                    git_repo.git.checkout('main')
                    git_repo.git.reset('--hard')
                    git_repo.git.clean('-fd')
                    git_repo.git.fetch()
                    c = git_repo.git.rebase()
                    print(c)
                except Exception as e3:
                    exceptions.write(e3.__str__()+'\n')
                    paths.write(path_temp+'\n')


for index,row in df_2.iterrows():
    path1='/media/umd-002677/TOSHIBA EXT/PhD Work/repos/'+'applied'+'/'+row['ProjectName']
    path2='/media/umd-002677/TOSHIBA EXT/PhD Work/repos/'+'tool'+'/'+row['ProjectName']
    if(path.exists(path1)):
        path_temp = path1
    elif(path.exists(path2)):
        path_temp=path2
    else:
        exceptions.write('Paths Not Found: '+row['ProjectName']+'\n')
        continue
    # path='/media/umd-002677/TOSHIBA EXT/PhD Work/repos/no-ai-ml/CameloeAnthony/AndroidArchitectureCollection'
    # path='/media/umd-002677/TOSHIBA EXT/PhD Work/repos/no-ai-ml/12207480/TYCyclePagerView'
    try:
        print(path_temp)
        git_repo=Repo(path_temp)
        a=git_repo.git.pull()
        print(a)
    except Exception as e:
        print(e)
        git_repo = Repo(path_temp)
        try:
            print('retrying')
            print(path)
            git_repo.git.reset('--hard')
            git_repo.git.clean('-fd')
            b=git_repo.git.pull('--allow-unrelated-histories')
            print(b)
        except Exception as e1:
            print(e1)
            try:
                print('retrying again')
                git_repo.git.reset('--hard')
                git_repo.git.clean('-fd')
                git_repo.git.fetch()
                c= git_repo.git.rebase()
                print(c)
            except Exception as e2:
                print(e2)
                try:
                    print('retrying again again')
                    git_repo.git.checkout('main')
                    git_repo.git.reset('--hard')
                    git_repo.git.clean('-fd')
                    git_repo.git.fetch()
                    c = git_repo.git.rebase()
                    print(c)
                except Exception as e3:
                    exceptions.write(e3.__str__()+'\n')
                    paths.write(path_temp+'\n')



for index,row in df_3.iterrows():
    path1='/media/umd-002677/TOSHIBA EXT/PhD Work/repos/'+'no-ai-ml'+'/'+row['ProjectName']
    if(path.exists(path1)):
        path_temp = path1
    else:
        exceptions.write('Paths Not Found: '+row['ProjectName']+'\n')
        continue
    # path='/media/umd-002677/TOSHIBA EXT/PhD Work/repos/no-ai-ml/CameloeAnthony/AndroidArchitectureCollection'
    # path='/media/umd-002677/TOSHIBA EXT/PhD Work/repos/no-ai-ml/12207480/TYCyclePagerView'
    try:
        print(path_temp)
        git_repo=Repo(path_temp)
        a=git_repo.git.pull()
        print(a)
    except Exception as e:
        print(e)
        git_repo = Repo(path_temp)
        try:
            print('retrying')
            print(path)
            git_repo.git.reset('--hard')
            git_repo.git.clean('-fd')
            b=git_repo.git.pull('--allow-unrelated-histories')
            print(b)
        except Exception as e1:
            print(e1)
            try:
                print('retrying again')
                git_repo.git.reset('--hard')
                git_repo.git.clean('-fd')
                git_repo.git.fetch()
                c= git_repo.git.rebase()
                print(c)
            except Exception as e2:
                print(e2)
                try:
                    print('retrying again again')
                    git_repo.git.checkout('main')
                    git_repo.git.reset('--hard')
                    git_repo.git.clean('-fd')
                    git_repo.git.fetch()
                    c = git_repo.git.rebase()
                    print(c)
                except Exception as e3:
                    exceptions.write(e3.__str__()+'\n')
                    paths.write(path_temp+'\n')

# applied_in_dates_output=open('applied_commits_in_period.csv','w+',encoding='utf-8')
# applied_in_dates_output.write('ProjectRepo,ProjectRepoURL,ParentOfCommit,Commit')
# applied_in_dates_output.write('\n')
# applied_all_output=open('applied_commits_all.csv','w+',encoding='utf-8')
# applied_all_output.write('ProjectRepo,ProjectRepoURL,ParentOfCommit,Commit')
# applied_all_output.write('\n')
#
# tool_in_dates_output=open('tool_commits_in_period.csv','w+',encoding='utf-8')
# tool_in_dates_output.write('ProjectRepo,ProjectRepoURL,ParentOfCommit,Commit')
# tool_in_dates_output.write('\n')
# tool_all_output=open('tool_commits_all.csv','w+',encoding='utf-8')
# tool_all_output.write('ProjectRepo,ProjectRepoURL,ParentOfCommit,Commit')
# tool_all_output.write('\n')
#
# for index,row in df_ml.iterrows():
#     path='/'.join(row['TravisFilePath'].split('/')[:6])
#     print(path)
#     git_repo = git.repo.Repo(path,search_parent_directories=True)
#     try:
#         dates_file=open('../Project Stats Year/'+str(row['RepoType']+'/'+str(row['RepoName']).replace('/','_')+'/dates.csv'),'r',encoding='utf-8')
#         line_1=dates_file.readline().strip()
#         line_2=dates_file.readline().strip()
#         date_start= datetime.datetime.strptime(line_1, format)
#         date_end= datetime.datetime.strptime(line_2, format)
#     except Exception as e:
#         print(e)
#         continue
#     commits_list=git_repo.git.execute('git log --follow -- .travis.yml')
#     if str(row['RepoType']) == 'Applied':
#         all_output=applied_all_output
#         date_output=applied_in_dates_output
#     else:
#         all_output=tool_all_output
#         date_output=tool_in_dates_output
#     commit_hashs_list=[]
#     for line in commits_list.splitlines():
#         if 'commit ' in line:
#             commit_hash_temp=line.split(' ')[1].strip()
#             commit_hashs_list.append(commit_hash_temp)
#     tz_fixed = False
#     for commit_hash in commit_hashs_list:
#         commit_obj=git_repo.commit(rev=commit_hash)
#         try:
#             commit_prev= list(commit_obj.iter_parents())[0].hexsha
#         except:
#             commit_prev='None'
#         commit_date=commit_obj.committed_datetime
#         if tz_fixed == False:
#             date_end=date_end.replace(tzinfo=commit_date.timetz().tzinfo)
#             date_start=date_start.replace(tzinfo=commit_date.timetz().tzinfo)
#             tz_fixed=True
#         if commit_date<date_end and commit_date>date_start:
#            date_output.write(str(row['RepoName']+','+str(list(git_repo.remote().urls)[0])+','+str(commit_prev)+','+str(commit_hash)))
#            date_output.write('\n')
#         all_output.write(str(row['RepoName']+','+str(list(git_repo.remote().urls)[0])+','+str(commit_prev)+','+str(commit_hash)))
#         all_output.write('\n')










