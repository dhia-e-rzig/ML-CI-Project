import  pandas as pd
from os import path
import os
import shutil


out_dir='/home/umd-002677/PycharmProjects/ML-CI/ErrorLogsForManEval/'
rq2_list=pd.read_csv('logs_chosen_rand.csv')

for project in rq2_list['rand_logs'].tolist():
    print(project)
    # allpath = '/media/umd-002677/TOSHIBA EXT/PhD Work/repos/no-ai-ml'
    if path.exists(project):
        dirpath =  project
    else:
        print(project + ' --> FileNotFound')
        continue
    # for root, dirs, files in os.walk(dirpath):
    #     for file in files:
    #         if(file=='.travis.yml'):
    #             full_path=root+'/'+file
    #             out_path=out_dir+str(project).replace('/','_')+'_travis.yml'
    #             i = 1
    #             while(path.exists(out_path)):
    #                 out_path=out_dir+str(project).replace('/','_')+'_travis_'+str(i)+'_.yml'
    #                 i+=1
    shutil.copy(project,out_dir)
