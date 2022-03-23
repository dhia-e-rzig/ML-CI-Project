import pandas as pd
import regex
import os
import time
import _thread
import threading
from contextlib import contextmanager
from glob import glob

import multiprocessing as mp
import sys

class TimeoutException(Exception):
    def __init__(self, msg=''):
        self.msg = msg


@contextmanager
def time_limit(seconds, msg=''):
    timer = threading.Timer(seconds, lambda: _thread.interrupt_main())
    timer.start()
    try:
        yield
    except KeyboardInterrupt:
        raise TimeoutException("Timed out for operation {}".format(msg))
    finally:
        timer.cancel()

regexes_fail_csv=pd.read_csv('../../CSV Inputs/regex_failure_for_err.csv')
regexes_error_csv=pd.read_csv('../../CSV Inputs/regex_error.csv')

regexes_testfail_list=regexes_fail_csv.loc[regexes_fail_csv['Failure Type'] == 'Test Fail']['Regex'].to_list()
regexes_buildfail_list=regexes_fail_csv.loc[regexes_fail_csv['Failure Type'] == 'Build Error']['Regex'].to_list()
regexes_testerror_list=regexes_fail_csv.loc[regexes_fail_csv['Failure Type'] == 'Test Error']['Regex'].to_list()
regexes_cafail_list=regexes_fail_csv.loc[regexes_fail_csv['Failure Type'] == 'Code Analysis Error']['Regex'].to_list()
# regexes_travisfail_list=regexes_fail_csv.loc[regexes_fail_csv['Failure Type'] == 'Travis Error']['Regex'].to_list()
regexes_deploymenterror_list=regexes_fail_csv.loc[regexes_fail_csv['Failure Type'] == 'Deployment Error']['Regex'].to_list()
regexes_fail_csv.fillna(inplace=True, value="0")

regexes_testfail_addition_list=regexes_fail_csv.loc[regexes_fail_csv['Notes'].str.contains('can be test fail')]['Regex'].to_list()
regexes_testerror_addition_list=regexes_fail_csv.loc[regexes_fail_csv['Notes'].str.contains('can be test error')]['Regex'].to_list()

regexes_scripterror_list=[]#regexes_error_csv.loc[regexes_error_csv['Error Type'] == 'ScriptError']['Regex'].to_list()
regexes_builddependency_list=regexes_error_csv.loc[regexes_error_csv['Error Type'] == 'BuildDependencyError']['Regex'].to_list()
regexes_traviserror_list=[]#regexes_error_csv.loc[regexes_error_csv['Error Type'] == 'TravisError']['Regex'].to_list()


# print(len(regexes_travisfail_list))

# pprint(log_files)
# exit()



# pyflakes_mode=False
# TestFail=False
# BuildFail=False
# TestError=False
# CodeAnalysisError=False



class Log_failure_classifier():
    def __init__(self, file):
        self.file = file
        self.result = ""
    def process_file_with_regexes(self):
        file_name=self.file
        LogNotFound=False
        TimeExceeded=False
        NotPythonLang=False
        NoFailDetected = True
        pyflakes_mode = False
        TestFail = False
        BuildError = False
        TestError = False
        CodeAnalysisError = False
        DeploymentError = False
        TravisFail=False
        C_checks_error_mode=False
        No_output_travis_mode=False
        ErrorScanningMode = True
        FailMarkedAsError = False
        ScriptError = False
        script_error_subtype_list=[]
        BuildDependencyError = False
        build_dep_err_subtype_list=[]
        TravisError = True
        travis_error_subtype_list=[]

        print('processing ' + file_name)
        try:
            file = open(file_name, encoding='utf-8')
        except:
            print(file_name +'not found')
            return
        try:
            with time_limit(121):


                TestScanningMode=False
                CAScanningMode=False
                IgnoreMode=False
                list_test_fail_regexes_found = []
                list_test_error_regexes_found = []
                list_build_error_regexes_found = []
                list_ca_fail_regexes_found = []
                list_travis_fail_regexes_found = []
                list_deployment_error_regexes_found = []

                list_script_error_regexes_found = []
                list_build_dependency_error_regexes_found = []
                list_travis_error_regexes_found = []

                travis_error_job_error_mode=False
                for line in file:

                    if "Log Not Found" in line:
                        LogNotFound = True
                        return [str(str(file_name) + ',' + str(FailMarkedAsError) + ',' + str(ScriptError) + ',' + str(
                            BuildDependencyError) + ',' + str(TravisError) + ',' + str(
                            TimeExceeded) + ',' + str(NotPythonLang) + ',' + str(LogNotFound)),
                                str(str(file_name) + ';' + str('') + ';' + str(
                                    list_script_error_regexes_found) + ';' + str(
                                    list_build_dependency_error_regexes_found) + ';' + str(
                                    list_travis_error_regexes_found)
                                    )]
                   # exec_patt_1=regex.compile("====== <exec> ======")
                   # exec_patt_2=regex.compile("====== </exec> ======")
                   # if exec_patt_1.search(line):
                   #     IgnoreMode=True
                   # if exec_patt_2.search(line):
                   #     IgnoreMode=False
                   # if IgnoreMode:
                   #    continue

                    if ErrorScanningMode:
                        if not ScriptError:
                            for str_regex in regexes_scripterror_list:
                                if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                    str_regex = str_regex[1:-1]
                                # print(str_regex)
                                str_regex=str_regex.replace('""','"')
                                pattern = regex.compile(str_regex)
                                if pattern.search(line):
                                    ScriptError = True
                                    list_script_error_regexes_found.append(str_regex)


                        if not BuildDependencyError:
                            for str_regex in regexes_builddependency_list:
                                if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                    str_regex = str_regex[1:-1]
                                    # print(str_regex)
                                str_regex = str_regex.replace('""', '"')
                                if ";" in str_regex:
                                    str_regex_0=str_regex.split(';')[0]
                                    str_regex_1=str_regex.split(';')[1]
                                    pattern1=regex.compile(str_regex_0)
                                    pattern2=regex.compile(str_regex_1)
                                    if pattern1.search(line):
                                        C_checks_error_mode=True
                                    if pattern2.search(line) and C_checks_error_mode:
                                        BuildDependencyError = True
                                        list_build_dependency_error_regexes_found.append(line.replace(';',':'))
                                else:
                                    pattern = regex.compile(str_regex)
                                    if pattern.search(line):
                                        BuildDependencyError = True
                                        list_build_dependency_error_regexes_found.append(line.replace(';',':'))

                        if "Your build has been stopped" in line and len(
                                list_travis_error_regexes_found) == 0:  # testing for incomplete files
                            TravisError = False
                            try:
                                travis_error_subtype_list.remove('Incomplete Log')
                            except:
                                pass

                        for str_regex in regexes_traviserror_list:
                                if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                    str_regex = str_regex[1:-1]
                                    # print(str_regex)
                                str_regex = str_regex.replace('""', '"')
                                if ";" in str_regex:
                                    str_regex_0 = str_regex.split(';')[0]
                                    str_regex_1 = str_regex.split(';')[1]
                                    pattern1 = regex.compile(str_regex_0)
                                    pattern2 = regex.compile(str_regex_1)
                                    if pattern1.search(line):
                                        No_output_travis_mode = True
                                    if pattern2.search(line) and No_output_travis_mode:
                                        TravisError = True
                                        list_travis_error_regexes_found.append(str_regex)
                                else:
                                    pattern = regex.compile(str_regex)
                                    if pattern.search(line):
                                        TravisError = True
                                        print(pattern)
                                        list_travis_error_regexes_found.append(str_regex)

                if not (ScriptError  or BuildDependencyError):
                    file.seek(0,0)
                    for line in file:
                        if TestFail and len(list_test_fail_regexes_found) == 1 and list_test_fail_regexes_found[0]=="=+ FAILURES =+" and "FLAKE8" in line:
                            # print("FLAKEREM")
                            TestFail=False
                            list_test_fail_regexes_found.clear()

                        test_command_regex_0=r"0K\$ (?!pip)\b.* [A-Za-z]*test"
                        test_command_regex_1=r"0K\$ (?!pip)\b.* nose"
                        test_command_regex_2=r"0K\$ [A-Za-z]*sh ([^ !$`&*()+]|(\\[ !$`&*()+]))+([a-zA-Z0-9\s_\\.\-\(\):])*test([a-zA-Z0-9\s_\\.\-\(\):])*.sh"
                        test_command_regex_3=r"0K\$ python (-|--)?[A-za-z]* unittest"
                        # test_command_regex_4=r"0K\$ (?!pip)\b[A-Za-z]+test"
                        test_command_regex_5=r"0K\$.* (?!pip)\b[A-Za-z]*test"
                        pattern0 = regex.compile(test_command_regex_0)
                        pattern1 = regex.compile(test_command_regex_1)
                        pattern2 = regex.compile(test_command_regex_2)
                        pattern3 = regex.compile(test_command_regex_3)
                        # pattern4 = regex.compile(test_command_regex_4)
                        pattern5 = regex.compile(test_command_regex_5)
                        if("==== test session starts ===" in line )or(pattern0.search(line))or (pattern1.search(line)) or (pattern2.search(line)) or (pattern3.search(line)) or(pattern5.search(line)):#(pattern4.search(line))
                            # if(file_name=="152299145.txt"):
                            #     print(pattern1.search(line))
                            #     print(pattern2.search(line))
                            #     print(pattern3.search(line))
                            #     print(pattern4.search(line))
                            #     print(pattern5.search(line))
                            #     print(line)
                            #     exit()
                            FailMarkedAsError=True
                            TestScanningMode=True

                        # pattern1 = regex.compile("=+")
                        # pattern2 = regex.compile("error")
                        # pattern3 = regex.compile("in")
                        test_end_regex_1=r"^[^-\s].*=+ .* seconds ==="
                        test_end_regex_2=r"The command \"[A-Za-z]*sh ([^ !$`&*()+]|(\\[ !$`&*()+]))+([a-zA-Z0-9\s_\\.\-\(\):])*test([a-zA-Z0-9\s_\\.\-\(\):])*.sh\" exited"
                        pattern_end_1=regex.compile(test_end_regex_1)
                        pattern_end_2=regex.compile(test_end_regex_2)
                        if ("travis_time:end:" in line) or pattern_end_1.search(line) or pattern_end_2.search(line):
                            TestScanningMode=False
                        if ("Test if pep8 is respected") in line or ("0K$ coverage") in line or ("0K$ flake8") in line:
                            CAScanningMode=True
                            FailMarkedAsError=True
                            TestScanningMode=False
                        if("The command " in line) or ("travis_time:end:" in line):
                            CAScanningMode=False
                        # if ('Build language') in line and not (('python') in line or ('generic') in line):
                        #      print('build language is not python')
                        #      # lang_not_python_count += 1
                        #      # print('lang not python')
                        #      NotPythonLang=True
                        #      break
                        if not TestFail:
                             for str_regex in regexes_testfail_list:
                                 if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                     str_regex = str_regex[1:-1]
                                 # print(str_regex)
                                 str_regex = str_regex.replace('""', '"')
                                 pattern = regex.compile(str_regex)
                                 if pattern.search(line):
                                     TestFail = True
                                     list_test_fail_regexes_found.append(str_regex)
                                 # add testing to see if regexes are overlapping
                             if TestScanningMode:
                                 for str_regex in regexes_testfail_addition_list:
                                     if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                         str_regex = str_regex[1:-1]
                                     pattern = regex.compile(str_regex)
                                     if pattern.search(line):
                                         TestFail = True
                                         list_test_fail_regexes_found.append(str_regex)

                        if not BuildError:
                             regex_list=regexes_buildfail_list
                             if TestScanningMode or CAScanningMode:
                                 regex_list =[] #[i for i in regexes_buildfail_list if i not in regexes_testfail_addition_list]
                             for str_regex in regex_list:
                                 if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                     str_regex = str_regex[1:-1]
                                 str_regex = str_regex.replace('""', '"')
                                 pattern = regex.compile(str_regex)
                                 if pattern.search(line):
                                     BuildError = True
                                     list_build_error_regexes_found.append(str_regex)

                        if not TestError:
                             for str_regex in regexes_testerror_list:
                                 if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                     str_regex = str_regex[1:-1]
                                 str_regex = str_regex.replace('""', '"')
                                 pattern = regex.compile(str_regex)
                                 if pattern.search(line):
                                     TestError = True
                                     list_test_error_regexes_found.append(str_regex)
                             if TestScanningMode:
                                 for str_regex in regexes_testerror_addition_list:
                                     if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                         str_regex = str_regex[1:-1]
                                     str_regex = str_regex.replace('""', '"')
                                     pattern = regex.compile(str_regex)
                                     if pattern.search(line):
                                         TestFail = True
                                         list_test_fail_regexes_found.append(str_regex)


                        if not CodeAnalysisError:
                             for str_regex in regexes_cafail_list:
                                 if(';') in str_regex:
                                     if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                         str_regex = str_regex[1:-1]
                                     regex_arr = str_regex.split(';')
                                     pattern1 = regex.compile(regex_arr[0])
                                     pattern2 = regex.compile(regex_arr[1])
                                     if pattern1.search(line):
                                         pyflakes_mode = True
                                     if pyflakes_mode and pattern2.search(line):
                                         CodeAnalysisError = True
                                         list_ca_fail_regexes_found.append(str_regex)

                                 else:
                                     if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                         str_regex = str_regex[1:-1]
                                     pattern = regex.compile(str_regex)
                                     str_regex = str_regex.replace('""', '"')
                                     if pattern.search(line):
                                         CodeAnalysisError = True
                                         list_ca_fail_regexes_found.append(str_regex)
                             if CAScanningMode:
                                 for str_regex in regexes_testfail_addition_list:
                                     if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                          str_regex = str_regex[1:-1]
                                     pattern = regex.compile(str_regex)
                                     str_regex = str_regex.replace('""', '"')
                                     if pattern.search(line):
                                          CodeAnalysisError = True
                                          list_ca_fail_regexes_found.append(str_regex)



                        # for str_regex in regexes_travisfail_list:
                        #     if(str_regex[1] == '"' and str_regex[-1] =='"'):
                        #         str_regex=str_regex[1:-1]
                        #     pattern = regex.compile(str_regex)
                        #     str_regex = str_regex.replace('""', '"')
                        #     if pattern.search(line):
                        #         TravisFail = True
                        #         list_travis_fail_regexes_found.append(str_regex)

                        if not DeploymentError:
                             for str_regex in regexes_deploymenterror_list:
                                 if(str_regex[1] == '"' and str_regex[-1] =='"'):
                                     str_regex=str_regex[1:-1]
                                 pattern = regex.compile(str_regex)
                                 str_regex = str_regex.replace('""', '"')
                                 if pattern.search(line):
                                     DeploymentError = True
                                     list_deployment_error_regexes_found.append(str_regex)
                if not (BuildError or TestFail or TestError or CodeAnalysisError or TravisFail or DeploymentError ) and ( TravisError and TravisFail):
                    TravisFail=False
                   # if (len(list_test_fail_regexes_found)>1):
                   #      with open('regex_together_test_fail.csv','a+',encoding='utf-8') as f:
                   #          f.write(str(list_test_fail_regexes_found))
                   #          f.write('\n')
                   # if (len(list_test_error_regexes_found)>1):
                   #     with open('regex_together_test_error.csv','a+',encoding='utf-8') as f:
                   #         f.write(str(list_test_error_regexes_found))
                   #         f.write('\n')
                   # if (len(list_build_error_regexes_found)>1):
                   #     with open('regex_together_build_fail.csv','a+',encoding='utf-8') as f:
                   #          f.write(str(list_build_error_regexes_found))
                   #          f.write('\n')
                   # if (len(list_ca_fail_regexes_found) > 1):
                   #     with open('regex_together_ca_error.csv', 'a+', encoding='utf-8') as f:
                   #         f.write(str(list_ca_fail_regexes_found))
                   #         f.write('\n')
                   # if (len(list_test_error_regexes_found) > 1):
                   #     with open('regex_together_travis_error.csv', 'a+', encoding='utf-8') as f:
                   #         f.write(str(list_test_error_regexes_found))
                   #         f.write('\n')
        except Exception as e:
            # time_exceeded_count += 1

            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            # exit()
            TimeExceeded=True
            print('time limit exceded for file: ' + file_name)
        if (not FailMarkedAsError):
            FailMarkedAsError = BuildError or TestFail or TestError or CodeAnalysisError or TravisFail or DeploymentError
        print(str(file_name) + ' processed')

        list_fails=[]

        if FailMarkedAsError:
            ScriptError= False
            TravisError = False
            BuildDependencyError = False
            list_fails=list_test_fail_regexes_found+list_build_error_regexes_found+list_travis_fail_regexes_found+list_deployment_error_regexes_found+list_ca_fail_regexes_found+list_test_error_regexes_found
        return [str(str(file_name) + ',' + str(FailMarkedAsError) + ',' + str(ScriptError) + ',' + str(
            BuildDependencyError) + ',' + str(TravisError) + ',' + str(
            TimeExceeded) + ',' + str(NotPythonLang)+','+str(LogNotFound)),
                str(str(file_name) +';'+str(list_fails)+ ';' + str(list_script_error_regexes_found) + ';' + str(
                    list_build_dependency_error_regexes_found) + ';' + str(list_travis_error_regexes_found)
                   )]
        # csv_res.write('\n')


    # def my_process(self, multiply_by, add_to):
    #     self.result = self.input * multiply_by
    #     self._my_sub_process(add_to)
    #     return self.result
    #
    # def _my_sub_process(self, add_to):
    #     self.result += add_to


NUM_CORE = mp.cpu_count()

def worker(arg):
    obj= arg
    return obj.process_file_with_regexes()

if __name__ == "__main__":
    start_time_all = time.perf_counter()
    # log_files = os.listdir('../../ErroredLogs-ForMining')
    # all_job_logs = [y for x in os.walk('C:\\Users\\dhiarzig\\PycharmProjects\\ML-CI\\Project Stats Year') for y in
    #                 glob(os.path.join(x[0], '*.txt'))]
    # all_job_csv = [y for x in os.walk('C:\\Users\\dhiarzig\\PycharmProjects\\ML-CI\\Project Stats Year') for y in
    #                glob(os.path.join(x[0], 'job_detailed_info.csv'))]
    # print(all_job_csv[:10])
    # print(all_job_logs[:10])
    # repeat_project_list_a = pd.read_csv('repeat_stats.csv')['RepoName'].to_list()
    # repeat_project_list = [str(x).replace('/', '_') for x in repeat_project_list_a]
    # repeat_job_logs = [y for y in all_job_logs if str(y).split('\\')[7] in repeat_project_list]
    # repeat_job_csv = [y for y in all_job_csv if str(y).split('\\')[7] in repeat_project_list]
    # pd_errors_logs_set1=pd.read_csv('..\..\CSV Outputs\error_classification_nonml.csv')
    # pd_errors_logs_set2=pd.read_csv('..\..\CSV Outputs\error_classification_additional_08_17_2021.csv')
    # list_jobs_errored= []
    # for job_csv in repeat_job_csv:
    #     try:
    #         df_csv = pd.read_csv(job_csv)
    #         failed_jobs = df_csv[df_csv['JobState'] == 'errored']['JobID'].to_list()
    #         failed_jobs = [str(x) + '.txt' for x in failed_jobs]
    #         list_jobs_failed.extend(failed_jobs)
    #     except:
    #         continue
    # print(list_jobs_failed[:10])
    # job_failed_logs = [x for x in repeat_job_logs if str(x).split('\\')[-1] in list_jobs_failed]
    # df_csv = pd.read_csv('../../unclassified_err2_.csv')
    # job_failed_logs = df_csv['Path'].to_list()
    # print(pd_errors_logs_set1.columns)
    all_job_logs = [y for x in os.walk('../../Project Stats Year/NonML/') for y in
                    glob(os.path.join(x[0], '*.txt'))]
    all_job_csv = [y for x in os.walk('../../Project Stats Year/NonML/') for y in
                   glob(os.path.join(x[0], 'job_detailed_info.csv'))]
    list_jobs_errored = []
    for job_csv in all_job_csv:
        try:
            df_csv = pd.read_csv(job_csv)
            failed_jobs = df_csv[df_csv['JobState'] == 'errored']['JobID'].to_list()
            failed_jobs = [str(x) + '.txt' for x in failed_jobs]
            list_jobs_errored.extend(failed_jobs)
        except:
            continue
    job_errored_logs = [x for x in all_job_logs if str(x).split('/')[-1] in list_jobs_errored]
    # print(pd_errors_logs_set2.columns)
    # job_errored_logs=pd_errors_logs_set1[pd_errors_logs_set1['BuildDepError']==True]['file_name'].to_list()+pd_errors_logs_set2[pd_errors_logs_set2['BuildDepError']==True]['file_name'].to_list()
    list_of_objects = [Log_failure_classifier(i) for i in job_errored_logs]
    pool = mp.Pool(NUM_CORE)
    list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()

    # csv_res = open('../../CSV Outputs/error_classification_all_08_04_2021.csv', 'w+')
    # csv_res.write('file_name,FailureClassedAsError,ScriptError,BuildDepError,TravisError,TimeExceeded,NotPythonLang,LogNotFound')
    # csv_res.write('\n')
    # for line in list_of_results:
    #     line=line[0]
    #     csv_res.write(line)
    #     csv_res.write('\n')
    csv_out = open('../../CSV Outputs/error_classification_nonml_03_18_2022_v1.csv', 'w+')
    #hen we tested each of these detection scripts on sets of manually labeled 100 errored logs and 100 failed logs, different from the remaining sets of files, and which achieved an average (precision,recall,  F-1) on each of the Job failure and Job error sub-types.
    csv_out.write('file_name,FailureClassedAsError,ScriptError,BuildDepError,TravisError,TimeExceeded,NotPythonLang,LogNotFound')
    csv_out.write('\n')
    for line_t in list_of_results:
        if line_t is None:
            continue
        line = line_t[0]
        csv_out.write(line)
        csv_out.write('\n')
    end_time_all = time.perf_counter()
    print(f"Execution Time : {end_time_all - start_time_all:0.6f}")


