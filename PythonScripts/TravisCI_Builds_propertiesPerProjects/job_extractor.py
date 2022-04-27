import pandas as pd

from PythonScripts.Utils.Travis_Utils import get_travis_build

df_fail_ml=pd.read_csv('fail_ids_to_filter_ml.csv')
df_error_ml=pd.read_csv('error_ids_to_filter_ml.csv')

df_fail_nonml=pd.read_csv('fail_ids_to_filter_nonml.csv')
df_error_nonml=pd.read_csv('error_ids_to_filter_nonml.csv')


excep_out=open('job-exceptions.txt','w+')

builds_fail_list=df_fail_ml['id'].tolist()
out = open('fail_job_ids_to_filter_ml.csv','w+')
for fail_build in builds_fail_list:
    try:
        # print(fail_build)
        build = get_travis_build(fail_build)
        print(build.id)
        list_jobs=build.jobs
        for job in list_jobs:
            try:
                out.write(str(job.id))
                out.write('\n')
            except Exception as e:
                print(e)
                continue
    except Exception as e:
        excep_out.write(str(e))
        excep_out.write('\n')
        continue


builds_error_list=df_error_ml['id'].tolist()
out = open('error_job_ids_to_filter_ml.csv','w+')
for error_build in builds_error_list:
    try:
        # print(fail_build)
        build = get_travis_build(error_build)
        print(build.id)
        list_jobs=build.jobs
        for job in list_jobs:
            try:
                out.write(str(job.id))
                out.write('\n')
            except Exception as e:
                print(e)
                continue
    except Exception as e:
        excep_out.write(str(e))
        excep_out.write('\n')
        continue

builds_fail_list = df_fail_nonml['id'].tolist()
out = open('fail_job_ids_to_filter_nonml.csv', 'w+')
for build_fail in builds_fail_list:
    try:
        # print(fail_build)
        build = get_travis_build(build_fail)
        print(build.id)
        list_jobs = build.jobs
        for job in list_jobs:
            try:
                out.write(str(job.id))
                out.write('\n')
            except Exception as e:
                print(e)
                continue
    except Exception as e:
        excep_out.write(str(e))
        excep_out.write('\n')
        continue

builds_error_list=df_error_nonml['id'].tolist()
out = open('error_job_ids_to_filter_nonml.csv','w+')
for error_build in builds_error_list:
    try:
        # print(fail_build)
        build = get_travis_build(error_build)
        print(build.id)
        list_jobs=build.jobs
        for job in list_jobs:
            try:
                out.write(str(job.id))
                out.write('\n')
            except Exception as e:
                print(e)
                continue
    except Exception as e:
        excep_out.write(str(e))
        excep_out.write('\n')
        continue