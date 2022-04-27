import pandas as pd
import regex
import os
import time
import _thread
import threading
from contextlib import contextmanager
from glob import glob
from PythonScripts.TravisCI_BuildBreak_Log_Analysis.line_extractor.failure_extractor import collect_lines

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


regexes_csv = pd.read_csv('../../../CSV Input - New/regex_failure_v2.csv')
regexes_testfail_list = regexes_csv.loc[regexes_csv['Failure Type'] == 'Test Fail'][['Regex','SubType']].values.tolist()
regexes_buildfail_list = regexes_csv.loc[regexes_csv['Failure Type'] == 'Build Error'][['Regex','SubType']].values.tolist()
regexes_testerror_list = regexes_csv.loc[regexes_csv['Failure Type'] == 'Test Error'][['Regex','SubType']].values.tolist()
regexes_cafail_list = regexes_csv.loc[regexes_csv['Failure Type'] == 'Code Analysis Error'][['Regex','SubType']].values.tolist()
regexes_travisfail_list = regexes_csv.loc[regexes_csv['Failure Type'] == 'Travis Error'][['Regex','SubType']].values.tolist()
regexes_deploymenterror_list = regexes_csv.loc[regexes_csv['Failure Type'] == 'Deployment Error'][['Regex','SubType']].values.tolist()
regexes_csv.fillna(inplace=True, value="0")
regexes_testfail_addition_list = regexes_csv.loc[regexes_csv['Notes'].str.contains('can be test fail')][['Regex','SubType']].values.tolist()
regexes_testerror_addition_list = regexes_csv.loc[regexes_csv['Notes'].str.contains('can be test error')][['Regex','SubType']].values.tolist()


# pyflakes_mode=False
# TestFail=False
# BuildFail=False
# TestError=False
# CodeAnalysisError=False

#
# def get_regex_subtype(str_regex):
#     subtype = regexes_csv.loc[regexes_csv['Regex'] == str_regex]['SubType'].to_list()[0]
#     return subtype


def get_first_non_general_subtype(subtype_list):
    General_subtypes=[]
    for sub_type in subtype_list:
        if 'general' not in str(sub_type).lower():
            return sub_type
        General_subtypes.append(sub_type)
    if len(subtype_list) ==0:
        return None
    return General_subtypes[0]


class Log_failure_classifier():
    def __init__(self, file):
        self.file = file
        self.result = ""

    def process_file_with_regexes(self):
        file_name = self.file
        LogNotFound = False
        TimeExceeded = False
        NotPythonLang = False
        NoFailDetected = True
        pyflakes_mode = False
        TestFail = False
        BuildError = False
        TestError = False
        CodeAnalysisError = False
        DeploymentError = False
        slow_mode = True
        TravisError = True  # testing for incomplete files
        print('processing ' + file_name)
        file = open(file_name, encoding='utf-8')  # os.path.join('../../FailedLogs-ForAccuracyTesting2',
        contents = file.read()
        lines = contents.split('\n')
        No_output_travis_mode=False
        try:
            with time_limit(61):
                TestScanningMode = False
                CAScanningMode = False
                IgnoreMode = False
                list_test_fail_regexes_found = []
                list_test_error_regexes_found = []
                list_build_error_regexes_found = []
                list_ca_fail_regexes_found = []
                list_travis_fail_regexes_found = []
                list_deployment_error_regexes_found = []
                test_fail_subtype_list = []
                build_error_subtype_list = []
                test_error_subtype_list = []
                ca_fail_subtype_list = []
                travis_fail_subtype_list = ['Incomplete Log']
                deployment_error_subtype_list = []
                list_test_fail_lines_found = []
                list_test_error_lines_found = []
                list_build_error_lines_found = []
                list_ca_fail_lines_found = []
                list_travis_fail_lines_found = []
                list_deployment_error_lines_found = []

                for i in range(0, len(lines)):
                    line = lines[i]
                    # exec_patt_1=regex.compile("====== <exec> ======")
                    # exec_patt_2=regex.compile("====== </exec> ======")
                    # if exec_patt_1.search(line):
                    #     IgnoreMode=True
                    # if exec_patt_2.search(line):
                    #     IgnoreMode=False
                    # if IgnoreMode:
                    #    continue

                    if TestFail and len(list_test_fail_regexes_found) == 1 and list_test_fail_regexes_found[
                        0] == "=+ FAILURES =+" and "FLAKE8" in line:
                        # print("FLAKEREM")
                        TestFail = False
                        list_test_fail_regexes_found.clear()
                    if "Done. Your build exited with" in line and len(
                            list_travis_fail_regexes_found) == 0:  # testing for incomplete files
                        TravisError = False
                        travis_fail_subtype_list.remove('Incomplete Log')
                    if "Log Not Found" in line:
                        LogNotFound = True
                        NoFailDetected = not (
                                BuildError or TestFail or TestError or CodeAnalysisError or TravisError or DeploymentError)
                        return [str(str(file_name) + ',' + str(TestFail) + ',' + str(BuildError) + ',' + str(
                            TestError) + ',' + str(
                            CodeAnalysisError) + ',' + str(TravisError) + ',' + str(DeploymentError) + ',' + str(
                            NoFailDetected) + ',' + str(
                            TimeExceeded) + ',' + str(NotPythonLang)) + ',' + str(LogNotFound),
                                str(str(file_name) + ';' + str(test_fail_subtype_list) + ';' + str(
                                    build_error_subtype_list) + ';' + str(test_error_subtype_list)
                                    + ';' + str(ca_fail_subtype_list) + ';' + str(
                                    travis_fail_subtype_list) + ';' + str(deployment_error_subtype_list)),
                                str(str(file_name) + ';' + str(
                                    get_first_non_general_subtype(test_fail_subtype_list)) + ';' + str(
                                    get_first_non_general_subtype(build_error_subtype_list)) + ';' + str(
                                    get_first_non_general_subtype(test_error_subtype_list))
                                    + ';' + str(get_first_non_general_subtype(ca_fail_subtype_list)) + ';' + str(
                                    get_first_non_general_subtype(
                                        travis_fail_subtype_list)) + ';' + str(
                                    get_first_non_general_subtype(deployment_error_subtype_list))),
                                [str(file_name), list_test_fail_lines_found,
                                 list_build_error_lines_found, list_test_error_lines_found, list_ca_fail_lines_found,
                                 list_travis_fail_lines_found, list_deployment_error_lines_found]

                                ]
                    if TestFail and BuildError and TestError and CodeAnalysisError and TravisError and DeploymentError:
                        NoFailDetected = not (
                                BuildError or TestFail or TestError or CodeAnalysisError or TravisError or DeploymentError)
                        return [str(str(file_name) + ',' + str(TestFail) + ',' + str(BuildError) + ',' + str(
                            TestError) + ',' + str(
                            CodeAnalysisError) + ',' + str(TravisError) + ',' + str(DeploymentError) + ',' + str(
                            NoFailDetected) + ',' + str(
                            TimeExceeded) + ',' + str(NotPythonLang)) + ',' + str(LogNotFound),
                                str(str(file_name) + ';' + str(test_fail_subtype_list) + ';' + str(
                                    build_error_subtype_list) + ',' + str(test_error_subtype_list)
                                    + ';' + str(ca_fail_subtype_list) + ';' + str(
                                    travis_fail_subtype_list) + ';' + str(deployment_error_subtype_list)),
                                str(str(file_name) + ';' + str(
                                    get_first_non_general_subtype(test_fail_subtype_list)) + ';' + str(
                                    get_first_non_general_subtype(build_error_subtype_list)) + ';' + str(
                                    get_first_non_general_subtype(test_error_subtype_list))
                                    + ';' + str(get_first_non_general_subtype(ca_fail_subtype_list)) + ';' + str(
                                    get_first_non_general_subtype(
                                        travis_fail_subtype_list)) + ';' + str(
                                    get_first_non_general_subtype(deployment_error_subtype_list))),
                                [str(file_name), list_test_fail_lines_found,
                                 list_build_error_lines_found, list_test_error_lines_found, list_ca_fail_lines_found,
                                 list_travis_fail_lines_found, list_deployment_error_lines_found]
                                ]
                    test_command_regex_0 = r"0K\$ (?!pip)\b.* [A-Za-z]*test"
                    test_command_regex_1 = r"0K\$ (?!pip)\b.* nose"
                    test_command_regex_2 = r"0K\$ [A-Za-z]*sh ([^ !$`&*()+]|(\\[ !$`&*()+]))+([a-zA-Z0-9\s_\\.\-\(\):])*test([a-zA-Z0-9\s_\\.\-\(\):])*.sh"
                    test_command_regex_3 = r"0K\$ python (-|--)?[A-za-z]* unittest"

                    test_command_regex_4 = "py(\.)?test .*tests"
                    test_command_regex_5 = r"0K\$.* (?!pip)\b[A-Za-z]*test"
                    pattern0 = regex.compile(test_command_regex_0)
                    pattern1 = regex.compile(test_command_regex_1)
                    pattern2 = regex.compile(test_command_regex_2)
                    pattern3 = regex.compile(test_command_regex_3)
                    pattern4=regex.compile(test_command_regex_4)
                    pattern5 = regex.compile(test_command_regex_5)
                    if ("==== test session starts ===" in line) or ("flask test" in line) or("tox -e" in line) or(
                    pattern0.search(line)) or (pattern1.search(line)) or (pattern2.search(line)) or (
                    pattern3.search(line)) or (pattern4.search(line))or (pattern5.search(line)):

                        TestScanningMode = True
                    test_end_regex_1 = r"^[^-\s].*=+ .* seconds ==="
                    test_end_regex_2 = r"The command \"[A-Za-z]*sh ([^ !$`&*()+]|(\\[ !$`&*()+]))+([a-zA-Z0-9\s_\\.\-\(\):])*test([a-zA-Z0-9\s_\\.\-\(\):])*.sh\" exited"
                    pattern_end_1 = regex.compile(test_end_regex_1)
                    pattern_end_2 = regex.compile(test_end_regex_2)
                    if ("travis_time:end:" in line) or pattern_end_1.search(line) or pattern_end_2.search(line):
                        TestScanningMode = False
                    if ("Test if pep8 is respected") in line or ("0K$ coverage") in line or ("0K$ flake8") in line:
                        CAScanningMode = True
                        TestScanningMode = False
                    if ("The command " in line) or ("travis_time:end:" in line):
                        CAScanningMode = False
                    if  slow_mode or not TestFail:
                        for tup in regexes_testfail_list:
                            str_regex=tup[0]
                            sub_type =tup[1]
                            if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                str_regex = str_regex[1:-1]
                            str_regex = str_regex.replace('""', '"')
                            # print(str_regex)
                            pattern = regex.compile(str_regex)
                            if pattern.search(line):
                                TestFail = True
                                list_test_fail_regexes_found.append(str_regex)
                                test_fail_subtype_list.append(sub_type)
                                list_test_fail_lines_found.append(collect_lines(i, lines))
                                break
                            # add testing to see if regexes are overlapping
                        if TestScanningMode:
                            for tup in regexes_testfail_addition_list:
                                str_regex = tup[0]
                                sub_type = tup[1]
                                if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                    str_regex = str_regex[1:-1]
                                str_regex = str_regex.replace('""', '"')
                                pattern = regex.compile(str_regex)
                                if pattern.search(line):
                                    TestFail = True
                                    list_test_fail_regexes_found.append(str_regex)
                                    test_fail_subtype_list.append(sub_type)
                                    list_test_fail_lines_found.append(collect_lines(i, lines))
                                    break

                    if  slow_mode or not BuildError:
                        regex_list = regexes_buildfail_list
                        if TestScanningMode or CAScanningMode:
                            regex_list = []  # [i for i in regexes_buildfail_list if i not in regexes_testfail_addition_list]
                        for tup in regex_list:
                            str_regex = tup[0]
                            sub_type = tup[1]
                            if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                str_regex = str_regex[1:-1]
                            str_regex = str_regex.replace('""', '"')
                            pattern = regex.compile(str_regex)
                            if pattern.search(line):
                                BuildError = True
                                list_build_error_regexes_found.append(str_regex)
                                build_error_subtype_list.append(sub_type)
                                list_build_error_lines_found.append(collect_lines(i, lines))
                                break

                    if  slow_mode or not TestError:
                        for tup in regexes_testerror_list:
                            str_regex = tup[0]
                            sub_type = tup[1]
                            if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                str_regex = str_regex[1:-1]
                            str_regex = str_regex.replace('""', '"')
                            pattern = regex.compile(str_regex)
                            if pattern.search(line):
                                TestError = True
                                test_error_subtype_list.append(sub_type)
                                list_test_error_regexes_found.append(str_regex)
                                list_test_error_lines_found.append(collect_lines(i, lines))
                                break
                        if TestScanningMode:
                            for tup in regexes_testerror_addition_list:
                                str_regex = tup[0]
                                sub_type = tup[1]
                                if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                    str_regex = str_regex[1:-1]
                                str_regex = str_regex.replace('""', '"')
                                pattern = regex.compile(str_regex)
                                if pattern.search(line):
                                    TestError = True
                                    test_error_subtype_list.append(sub_type)
                                    list_test_error_regexes_found.append(str_regex)
                                    list_test_error_lines_found.append(collect_lines(i, lines))
                                    break

                    if  slow_mode or not CodeAnalysisError:
                        for tup in regexes_cafail_list:
                            str_regex = tup[0]
                            sub_type = tup[1]
                            if (';') in str_regex:
                                if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                    str_regex = str_regex[1:-1]
                                str_regex = str_regex.replace('""', '"')
                                regex_arr = str_regex.split(';')
                                pattern1 = regex.compile(regex_arr[0])
                                pattern2 = regex.compile(regex_arr[1])
                                if pattern1.search(line):
                                    pyflakes_mode = True
                                if pyflakes_mode and pattern2.search(line):
                                    CodeAnalysisError = True
                                    ca_fail_subtype_list.append(sub_type)
                                    list_ca_fail_regexes_found.append(str_regex)
                                    list_ca_fail_lines_found.append(collect_lines(i, lines))
                                    break
                            else:
                                if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                    str_regex = str_regex[1:-1]
                                str_regex = str_regex.replace('""', '"')
                                pattern = regex.compile(str_regex)
                                if pattern.search(line):
                                    CodeAnalysisError = True
                                    list_ca_fail_regexes_found.append(str_regex)
                                    ca_fail_subtype_list.append(sub_type)
                                    list_ca_fail_lines_found.append(collect_lines(i, lines))
                                    break
                        if CAScanningMode:
                            for tup in regexes_testfail_addition_list:
                                str_regex = tup[0]
                                sub_type = tup[1]
                                if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                    str_regex = str_regex[1:-1]
                                str_regex = str_regex.replace('""', '"')
                                pattern = regex.compile(str_regex)
                                if pattern.search(line):
                                    CodeAnalysisError = True
                                    list_ca_fail_regexes_found.append(str_regex)
                                    ca_fail_subtype_list.append(sub_type)
                                    list_ca_fail_lines_found.append(collect_lines(i, lines))
                                    break


                    for tup in regexes_travisfail_list:
                        str_regex = tup[0]
                        sub_type = tup[1]
                        if (str_regex[1] == '"' and str_regex[-1] == '"'):
                            str_regex = str_regex[1:-1]
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
                                list_travis_fail_regexes_found.append(str_regex)
                                try:
                                    travis_fail_subtype_list.remove('Incomplete Log')
                                except:
                                    pass
                        pattern = regex.compile(str_regex)
                        if pattern.search(line):
                            TravisError = True
                            list_travis_fail_regexes_found.append(str_regex)
                            try:
                                travis_fail_subtype_list.remove('Incomplete Log')
                            except:
                                pass
                            travis_fail_subtype_list.append(sub_type)
                            list_travis_fail_lines_found.append(collect_lines(i, lines))
                            break

                    if  slow_mode or not DeploymentError:
                        for tup in regexes_deploymenterror_list:
                            str_regex = tup[0]
                            sub_type = tup[1]
                            if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                str_regex = str_regex[1:-1]
                            str_regex = str_regex.replace('""', '"')
                            pattern = regex.compile(str_regex)
                            if pattern.search(line):
                                DeploymentError = True
                                list_deployment_error_regexes_found.append(str_regex)
                                deployment_error_subtype_list.append(sub_type)
                                tups = collect_lines(i, lines)
                                list_deployment_error_lines_found.append(tups)
                                break
        except Exception as e:
            # time_exceeded_count += 1
            print(e)
            # exit()
            TimeExceeded = True
            print('time limit exceded for file: ' + file_name)
        NoFailDetected = not (
                    BuildError or TestFail or TestError or CodeAnalysisError or TravisError or DeploymentError)
        print(str(file_name) + ' processed')
        return [str(str(file_name) + ',' + str(TestFail) + ',' + str(BuildError) + ',' + str(TestError) + ',' + str(
            CodeAnalysisError) + ',' + str(TravisError) + ',' + str(DeploymentError) + ',' + str(
            NoFailDetected) + ',' + str(TimeExceeded) + ',' + str(NotPythonLang) + ',' + str(LogNotFound)),
                str(str(file_name) + ';' + str(test_fail_subtype_list) + ';' + str(
                    build_error_subtype_list) + ',' + str(test_error_subtype_list)
                    + ';' + str(ca_fail_subtype_list) + ';' + str(
                    travis_fail_subtype_list) + ';' + str(deployment_error_subtype_list)),
                str(str(file_name) + ';' + str(get_first_non_general_subtype(test_fail_subtype_list)) + ';' + str(
                    get_first_non_general_subtype(build_error_subtype_list)) + ';' + str(
                    get_first_non_general_subtype(test_error_subtype_list))
                    + ';' + str(get_first_non_general_subtype(ca_fail_subtype_list)) + ';' + str(
                    get_first_non_general_subtype(
                        travis_fail_subtype_list)) + ';' + str(
                    get_first_non_general_subtype(deployment_error_subtype_list))),
                [str(file_name), list_test_fail_lines_found,
                 list_build_error_lines_found, list_test_error_lines_found, list_ca_fail_lines_found,
                 list_travis_fail_lines_found, list_deployment_error_lines_found]
                ]


import multiprocessing as mp

NUM_CORE = mp.cpu_count()


def worker(arg):
    obj = arg
    return obj.process_file_with_regexes()


if __name__ == "__main__":
    start_time_all = time.perf_counter()
    all_job_logs = [y for x in os.walk('../../../Project Stats Year/NonML/') for y in
                    glob(os.path.join(x[0], '*.txt'))]
    all_job_csv = [y for x in os.walk('../../../Project Stats Year/NonML/') for y in
                   glob(os.path.join(x[0], 'job_detailed_info.csv'))]

    # print(all_job_logs[:5])
    # print(all_job_csv[:5])
    # exit(1)
    # repeat_project_list_a=pd.read_csv('repeat_stats.csv')['RepoName'].to_list()
    # repeat_project_list=[str(x).replace('/','_') for x in repeat_project_list_a]
    # repeat_job_logs=[y for y in all_job_logs if str(y).split('\\')[7] in repeat_project_list]
    # repeat_job_csv=[y for y in all_job_csv if str(y).split('\\')[7] in repeat_project_list]
    # print(all_job_csv[:10])
    # print(all_job_logs[:10])
    list_jobs_failed = []
    for job_csv in all_job_csv:
        try:
            df_csv = pd.read_csv(job_csv)
            failed_jobs = df_csv[df_csv['JobState'] == 'failed']['JobID'].to_list()
            failed_jobs = [str(x) + '.txt' for x in failed_jobs]
            list_jobs_failed.extend(failed_jobs)
        except:
            continue
    # print(list_jobs_failed[:10])
    # exit()
    job_failed_logs = [x for x in all_job_logs if str(x).split('/')[-1] in list_jobs_failed]

    # print(job_failed_logs)
    # exit()
    # df_csv = pd.read_csv('../../unclassified4.csv')
    # job_failed_logs=df_csv['Path'].to_list()
    list_of_objects = [Log_failure_classifier(i) for i in job_failed_logs]
    pool = mp.Pool(NUM_CORE)
    list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()

    csv_res = open('../../../CSV Output - New/classification_nonml_fail_03_29_2022_v3.csv', 'w+')
    csv_res.write(
        'file_name,TestFail,BuildError,TestError,CodeAnalysisError,TravisError,DeploymentError,NoFailDetected,TimeExceeded,NotPythonLang,LogNotFound')
    csv_res.write('\n')
    for line in list_of_results:
        line = line[0]
        csv_res.write(line)
        csv_res.write('\n')
    csv_subtype = open('../../../CSV Output - New/classification_nonml_fail_03_29_2022_v3_subtypes.csv', 'w+')
    csv_subtype.write(
        'file_name;TestFail;BuildError;TestError;CodeAnalysisError;TravisError;DeploymentError')
    csv_subtype.write('\n')
    for line in list_of_results:
        line = line[1]
        csv_subtype.write(line)
        csv_subtype.write('\n')

    csv_1subtype = open('../../../CSV Output - New/classification_nonml_fail_03_29_2022_v3_first_subtype.csv', 'w+')
    csv_1subtype.write(
        'file_name;TestFail;BuildError;TestError;CodeAnalysisError;TravisError;DeploymentError')
    csv_1subtype.write('\n')
    for line in list_of_results:
        line = line[2]
        csv_1subtype.write(line)
        csv_1subtype.write('\n')
    # # csv_res_testfail = open('../../CSV Outputs/3liners_08_04_2021_testfail.txt', 'w+', encoding='utf-8')
    # # csv_res_scripterror = open('../../CSV Outputs/3liners_08_04_2021_scripterror.txt', 'w+', encoding='utf-8')
    # # csv_res_testerror = open('../../CSV Outputs/3liners_08_04_2021_testerror.txt', 'w+', encoding='utf-8')
    # # csv_res_caerror = open('../../CSV Outputs/3liners_08_04_2021_caerror.txt', 'w+', encoding='utf-8')
    # # csv_res_deploymenterror = open('../../CSV Outputs/3liners_08_04_2021_deploymenterror.txt', 'w+', encoding='utf-8')
    # # csv_res_traviserror = open('../../CSV Outputs/3liners_08_04_2021_traviserror_USETHISONE.txt', 'w+', encoding='utf-8')
    # # for line in list_of_results:
    # #     res_line=line[3]
    # #     # print(res_line)
    # #     # exit()
    # #     file_name=res_line[0]
    # #     test_fails=res_line[1]
    # #     build_error=res_line[2]
    # #     test_errors=res_line[3]
    # #     ca_fails=res_line[4]
    # #     travis_errors=res_line[5]
    # #     deploy_fails=res_line[6]
    # #     if(len(test_fails) > 0):
    # #         csv_res_testfail.write("==============="+str(file_name)+"================")
    # #         csv_res_testfail.write('\n')
    # #         for tup in test_fails:
    # #             for line in tup:
    # #                 try:
    # #                     csv_res_testfail.write(str(line))
    # #                     csv_res_testfail.write('\n')
    # #                 except:
    # #                     continue
    # #     if (len(build_error) > 0):
    # #         csv_res_scripterror.write("===============" + str(file_name) + "================")
    # #         csv_res_scripterror.write('\n')
    # #         for tup in build_error:
    # #             for line in tup:
    # #                 try:
    # #                     csv_res_scripterror.write(str(line))
    # #                     csv_res_scripterror.write('\n')
    # #                 except:
    # #                     continue
    # #     if (len(test_errors) > 0):
    # #         csv_res_testerror.write("===============" + str(file_name) + "================")
    # #         csv_res_testerror.write('\n')
    # #         for tup in test_errors:
    # #             for line in tup:
    # #                 try:
    # #                     csv_res_testerror.write(str(line))
    # #                     csv_res_testerror.write('\n')
    # #                 except:
    # #                     continue
    # #     if (len(ca_fails) > 0):
    # #         csv_res_caerror.write("===============" + str(file_name) + "================")
    # #         csv_res_caerror.write('\n')
    # #         for tup in ca_fails:
    # #             for  line in tup:
    # #                 try:
    # #                     csv_res_caerror.write(str(line))
    # #                     csv_res_caerror.write('\n')
    # #                 except:
    # #                     continue
    # #     if (len(deploy_fails) > 0):
    # #         csv_res_deploymenterror.write("===============" + str(file_name) + "================")
    # #         csv_res_deploymenterror.write('\n')
    # #         for tup in deploy_fails:
    # #             for  line in tup:
    # #                 try:
    # #                     csv_res_deploymenterror.write(str(line))
    # #                     csv_res_deploymenterror.write('\n')
    # #                 except:
    # #                     continue
    # #     if (len(travis_errors) > 0):
    # #         csv_res_traviserror.write("===============" + str(file_name) + "================")
    # #         csv_res_traviserror.write('\n')
    # #         for tup in travis_errors:
    # #             for line in tup:
    # #                 try:
    # #                     csv_res_traviserror.write(str(line))
    # #                     csv_res_traviserror.write('\n')
    # #                 except:
    # #                     continue
    # end_time_all = time.perf_counter()
    # print(f"Execution Time : {end_time_all - start_time_all:0.6f}")


    #
    #.
    #
    # # repeat_project_list_a=pd.read_csv('repeat_stats.csv')['RepoName'].to_list()
    # # repeat_project_list=[str(x).replace('/','_') for x in repeat_project_list_a]
    # # repeat_job_logs=[y for y in all_job_logs if str(y).split('\\')[7] in repeat_project_list]
    # # repeat_job_csv=[y for y in all_job_csv if str(y).split('\\')[7] in repeat_project_list]
    # # print(all_job_csv[:10])
    # # print(all_job_logs[:10])
    # list_jobs_failed = []
    # for job_csv in all_job_csv:
    #     try:
    #         df_csv = pd.read_csv(job_csv)
    #         failed_jobs = df_csv[df_csv['JobState'] == 'failed']['JobID'].to_list()
    #         failed_jobs = [str(x) + '.txt' for x in failed_jobs]
    #         list_jobs_failed.extend(failed_jobs)
    #     except:
    #         continue
    # # print(list_jobs_failed[:10])
    # # exit()
    # job_failed_logs = [x for x in all_job_logs if str(x).split('/')[-1] in list_jobs_failed]
    #
    # # print(job_failed_logs)
    # # exit()
    # # df_csv = pd.read_csv('../../unclassified4.csv')
    # # job_failed_logs=df_csv['Path'].to_list()
    # list_of_objects = [Log_failure_classifier(i) for i in job_failed_logs]
    # pool = mp.Pool(NUM_CORE)
    # list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    # pool.close()
    # pool.join()
    #
    # csv_res = open('../../../CSV Output - New/classification_applied_fail_redo_projs_03_29_2022_v3_redo.csv', 'w+')
    # csv_res.write(
    #     'file_name,TestFail,BuildError,TestError,CodeAnalysisError,TravisError,DeploymentError,NoFailDetected,TimeExceeded,NotPythonLang,LogNotFound')
    # csv_res.write('\n')
    # for line in list_of_results:
    #     line = line[0]
    #     csv_res.write(line)
    #     csv_res.write('\n')
    # csv_subtype = open('../../../CSV Output - New/classification_applied_fail_redo_projs_03_29_2022_v3_subtypes_redo.csv', 'w+')
    # csv_subtype.write(
    #     'file_name;TestFail;BuildError;TestError;CodeAnalysisError;TravisError;DeploymentError')
    # csv_subtype.write('\n')
    # for line in list_of_results:
    #     line = line[1]
    #     csv_subtype.write(line)
    #     csv_subtype.write('\n')
    #
    # csv_1subtype = open('../../../CSV Output - New/classification_applied_fail_redo_projs_03_29_2022_v3_first_subtype_redo.csv', 'w+')
    # csv_1subtype.write(
    #     'file_name;TestFail;BuildError;TestError;CodeAnalysisError;TravisError;DeploymentError')
    # csv_1subtype.write('\n')
    # for line in list_of_results:
    #     line = line[2]
    #     csv_1subtype.write(line)
    #     csv_1subtype.write('\n')
    # end_time_all = time.perf_counter()
    #
    # list_projects = df_redo_repos['repo'].tolist()
    # start_time_all = time.perf_counter()
    # all_job_logs_raw = [y for x in os.walk('../../../Project Stats Year/Tool/') for y in
    #                     glob(os.path.join(x[0], '*.txt'))]
    #
    # all_job_csv_raw = [y for x in os.walk('../../../Project Stats Year/Tool/') for y in
    #                    glob(os.path.join(x[0], 'job_detailed_info.csv'))]
    # all_job_logs = []
    # all_job_csv = []
    # for proj in list_projects:
    #     temp_logs = [l for l in all_job_logs_raw if str(proj).lower() in str(l).lower()]
    #     temp_csv = [l for l in all_job_csv_raw if str(proj).lower() in str(l).lower()]
    #     all_job_logs.extend(temp_logs)
    #     all_job_csv.extend(temp_csv)
    #
    # # repeat_project_list_a=pd.read_csv('repeat_stats.csv')['RepoName'].to_list()
    # # repeat_project_list=[str(x).replace('/','_') for x in repeat_project_list_a]
    # # repeat_job_logs=[y for y in all_job_logs if str(y).split('\\')[7] in repeat_project_list]
    # # repeat_job_csv=[y for y in all_job_csv if str(y).split('\\')[7] in repeat_project_list]
    # # print(all_job_csv[:10])
    # # print(all_job_logs[:10])
    # list_jobs_failed = []
    # for job_csv in all_job_csv:
    #     try:
    #         df_csv = pd.read_csv(job_csv)
    #         failed_jobs = df_csv[df_csv['JobState'] == 'failed']['JobID'].to_list()
    #         failed_jobs = [str(x) + '.txt' for x in failed_jobs]
    #         list_jobs_failed.extend(failed_jobs)
    #     except:
    #         continue
    # # print(list_jobs_failed[:10])
    # # exit()
    # job_failed_logs = [x for x in all_job_logs if str(x).split('/')[-1] in list_jobs_failed]
    #
    # # print(job_failed_logs)
    # # exit()
    # # df_csv = pd.read_csv('../../unclassified4.csv')
    # # job_failed_logs=df_csv['Path'].to_list()
    # list_of_objects = [Log_failure_classifier(i) for i in job_failed_logs]
    # pool = mp.Pool(NUM_CORE)
    # list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    # pool.close()
    # pool.join()
    #
    # csv_res = open('../../../CSV Output - New/classification_tool_fail_redo_projs_03_29_2022_v3_redo.csv', 'w+')
    # csv_res.write(
    #     'file_name,TestFail,BuildError,TestError,CodeAnalysisError,TravisError,DeploymentError,NoFailDetected,TimeExceeded,NotPythonLang,LogNotFound')
    # csv_res.write('\n')
    # for line in list_of_results:
    #     line = line[0]
    #     csv_res.write(line)
    #     csv_res.write('\n')
    # csv_subtype = open('../../../CSV Output - New/classification_tool_fail_redo_projs_03_29_2022_v3_subtypes_redo.csv', 'w+')
    # csv_subtype.write(
    #     'file_name;TestFail;BuildError;TestError;CodeAnalysisError;TravisError;DeploymentError')
    # csv_subtype.write('\n')
    # for line in list_of_results:
    #     line = line[1]
    #     csv_subtype.write(line)
    #     csv_subtype.write('\n')
    #
    # csv_1subtype = open('../../../CSV Output - New/classification_tool_fail_redo_projs_03_29_2022_v3_first_subtype_redo.csv',
    #                     'w+')
    # csv_1subtype.write(
    #     'file_name;TestFail;BuildError;TestError;CodeAnalysisError;TravisError;DeploymentError')
    # csv_1subtype.write('\n')
    # for line in list_of_results:
    #     line = line[2]
    #     csv_1subtype.write(line)
    #     csv_1subtype.write('\n')
    # end_time_all = time.perf_counter()
    # print(f"Execution Time : {end_time_all - start_time_all:0.6f}")
