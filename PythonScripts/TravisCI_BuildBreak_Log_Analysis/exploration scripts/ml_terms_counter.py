import re
from pprint import pprint
import json
import numpy as np
import pandas as pd
import regex
import os
import time
import _thread
import threading
from contextlib import contextmanager
from glob import glob
from more_itertools import unique_everseen
import sys
import multiprocessing as mp

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

regexes_ml_csv=pd.read_csv('../../CSV Inputs/regex_ml_curated.csv')
regexes_ml_csv.fillna(inplace=True, value="0")
regexes_ml_list=regexes_ml_csv.loc[regexes_ml_csv['Type'] == 'ML']['Regex'].to_list()



regexes_csv = pd.read_csv('../../CSV Inputs/regex_failure.csv')
regexes_testfail_list = regexes_csv.loc[regexes_csv['Failure Type'] == 'Test Fail'][['Regex','SubType']].values.tolist()
regexes_csv.fillna(inplace=True,value="0")
regexes_testfail_addition_list = regexes_csv.loc[regexes_csv['Notes'].str.contains('can be test fail')][['Regex','SubType']].values.tolist()
regexes_buildfail_list = regexes_csv.loc[regexes_csv['Failure Type'] == 'Build Error'][['Regex','SubType']].values.tolist()
regexes_testerror_list = regexes_csv.loc[regexes_csv['Failure Type'] == 'Test Error'][['Regex','SubType']].values.tolist()
regexes_testerror_addition_list = regexes_csv.loc[regexes_csv['Notes'].str.contains('can be test error')][['Regex','SubType']].values.tolist()


def clean_line(str):
    op_string = re.sub(r'[^\w\s]', '', str)
    op_string = re.sub(r'[+-/*=]', '', op_string)
    return op_string
def collect_lines(i,lines):
    try:
        n=len(lines)
        if(i==0) and n>=3:
            line_0=lines[0]
            line_1=lines[1]
            line_2=lines[2]
            j=3
            while line_2.strip()=="" and j<n:
                j=j+1
                line_2=lines[j]
            while clean_line(line_2.strip())=="" and j<n:
                j=j+1
                line_2=lines[j]
            return(line_0,line_1,line_2)
        elif(i==0) and n==2:
            return (lines[0], lines[1])
        elif(i==(n-1)) and n>=3:
            line_0 = lines[i-2]
            line_1 = lines[i-1]
            line_2 = lines[i]
            j=i-2
            while line_0.strip()=="" and j>0:
                j=j-1
                line_0=lines[j]
            while clean_line(line_0.strip())=="" and j>0:
                j=j-1
                line_0=lines[j]
            j = i - 1
            while line_1.strip() == "" and j > 1:
                j = j - 1
                line_1 = lines[j]
            while clean_line(line_1.strip()) == "" and j > 1:
                j = j - 1
                line_1 = lines[j]
            return (line_0,line_1,line_2)
        elif(i==(n-1)) and n==2:
            return (lines[i - 1], lines[i])
        else:
            line_0 = lines[i - 1]
            line_1 = lines[i]
            line_2 =""
            if i==n-1  or lines[i +1].strip() =="":
                line_2=line_1
                line_1=line_0
                try:
                    line_0= lines[i - 2]
                except:
                    line_0=""
                j=i-2
                while clean_line(line_0.strip()) == "" and j > 1:
                    j = j - 1
                    line_0 = lines[j]
            else:
                line_2=lines[i+1]

            j=i - 1
            while line_0.strip() == "" and j > 0:
                j = j - 1
                line_0 = lines[j]
            while clean_line(line_0.strip()) == "" and j > 0:
                j = j - 1
                line_0 = lines[j]
            j = i + 1
            while line_2.strip() == "" and j < n-1:
                j = j + 1
                line_2 = lines[j]
            while clean_line(line_2.strip()) == "" and j < n - 1:
                j = j + 1
                line_2 = lines[j]

            return(line_0,line_1,line_2)
    except Exception as e:
        print(e)
        
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return

class Log_failure_classifier():
    def __init__(self, file,type):
        self.file = file
        self.type=type
        self.result = ""

    def process_file_with_regexes(self):
        if self.type=='fail':
            return self.process_file_with_regexes_fail()
        elif self.type=='test_error':
            return self.process_file_with_regexes_test_error()
        elif self.type=='build_error':
            return self.process_file_with_regexes_build_error()
        elif self.type == 'ml_fail':
            return self.process_file_with_regexes_fail_ml_all()
        else:
            print('Err type')

    def process_file_with_regexes_fail(self):
        file_name=self.file
        print('processing ' + file_name)
        file = open(os.path.join('', file_name), encoding='utf-8') #C:\Users\dhiarzig\PycharmProjects\ML-CI\Project Stats Year
        contents = file.read()
        lines= contents.split('\n')
        try:
            with time_limit(61):
                CAScanningMode = False
                TestScanningMode = False
                lines_tups_list = []
                for i in range(0, len(lines)):
                    line = lines[i]
                    test_command_regex_0 = r"0K\$ (?!pip)\b.* [A-Za-z]*test"
                    test_command_regex_1 = r"0K\$ (?!pip)\b.* nose"
                    test_command_regex_2 = r"0K\$ [A-Za-z]*sh ([^ !$`&*()+]|(\\[ !$`&*()+]))+([a-zA-Z0-9\s_\\.\-\(\):])*test([a-zA-Z0-9\s_\\.\-\(\):])*.sh"
                    test_command_regex_3 = r"0K\$ python (-|--)?[A-za-z]* unittest"

                    test_command_regex_5 = r"0K\$.* (?!pip)\b[A-Za-z]*test"
                    pattern0 = regex.compile(test_command_regex_0)
                    pattern1 = regex.compile(test_command_regex_1)
                    pattern2 = regex.compile(test_command_regex_2)
                    pattern3 = regex.compile(test_command_regex_3)

                    pattern5 = regex.compile(test_command_regex_5)
                    if ("==== test session starts ===" in line) or ("flask test" in line) or (
                            pattern0.search(line)) or (pattern1.search(line)) or (pattern2.search(line)) or (
                            pattern3.search(line)) or (pattern5.search(line)):  # (pattern4.search(line))

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

                    for tup in regexes_testfail_list:
                        str_regex = tup[0]
                        sub_type = tup[1]
                        if (str_regex[1] == '"' and str_regex[-1] == '"'):
                            str_regex = str_regex[1:-1]
                        str_regex = str_regex.replace('""', '"')
                        # print(str_regex)
                        pattern = regex.compile(str_regex)
                        if pattern.search(line):
                            lines_around=collect_lines(i, lines)
                            lines_tups_list.append(lines_around)
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
                                lines_around = collect_lines(i, lines)
                                lines_tups_list.append(lines_around)
                                break
                ml_found_around_list=[]
                # print('tups')
                # print(len(lines_tups_list))

                for i in range(0,len(lines_tups_list)):
                    tup=lines_tups_list[i]
                    for line in tup:
                        for str_regex in regexes_ml_list:
                            if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                str_regex = str_regex[1:-1]
                            # print(str_regex)
                            pattern = regex.compile(str_regex)
                            if pattern.search(line):
                                # TestFail = True
                                ml_found_around_list.append(tup)
                                i=i+1
                # print('ml tups')
                # print(len(ml_found_around_list))

                        # add testing to see if regexes are overlappingc
        except Exception as e:
            print("ERROR!")
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print('time limit exceded')
        return [self.file,ml_found_around_list]

    def process_file_with_regexes_build_error(self):
        file_name = self.file
        print('processing ' + file_name)
        file = open(os.path.join('', file_name),
                    encoding='utf-8')  # C:\Users\dhiarzig\PycharmProjects\ML-CI\Project Stats Year
        contents = file.read()
        lines = contents.split('\n')
        try:
            with time_limit(61):
                CAScanningMode = False
                TestScanningMode = False
                lines_tups_list = []
                for i in range(0, len(lines)):
                    line = lines[i]
                    test_command_regex_0 = r"0K\$ (?!pip)\b.* [A-Za-z]*test"
                    test_command_regex_1 = r"0K\$ (?!pip)\b.* nose"
                    test_command_regex_2 = r"0K\$ [A-Za-z]*sh ([^ !$`&*()+]|(\\[ !$`&*()+]))+([a-zA-Z0-9\s_\\.\-\(\):])*test([a-zA-Z0-9\s_\\.\-\(\):])*.sh"
                    test_command_regex_3 = r"0K\$ python (-|--)?[A-za-z]* unittest"

                    test_command_regex_5 = r"0K\$.* (?!pip)\b[A-Za-z]*test"
                    pattern0 = regex.compile(test_command_regex_0)
                    pattern1 = regex.compile(test_command_regex_1)
                    pattern2 = regex.compile(test_command_regex_2)
                    pattern3 = regex.compile(test_command_regex_3)

                    pattern5 = regex.compile(test_command_regex_5)
                    if ("==== test session starts ===" in line) or ("flask test" in line) or (
                            pattern0.search(line)) or (pattern1.search(line)) or (pattern2.search(line)) or (
                            pattern3.search(line)) or (pattern5.search(line)):  # (pattern4.search(line))

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
                            # list_build_error_regexes_found.append(str_regex)
                            lines_around = collect_lines(i, lines)
                            lines_tups_list.append(lines_around)
                            break
                ml_found_around_list = []
                # print(len(lines_tups_list))
                for i in range(0, len(lines_tups_list)):
                    tup = lines_tups_list[i]
                    for line in tup:
                        for str_regex in regexes_ml_list:
                            if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                str_regex = str_regex[1:-1]
                            # print(str_regex)
                            pattern = regex.compile(str_regex)
                            if pattern.search(line):
                                # TestFail = True
                                ml_found_around_list.append(tup)
                                i = i + 1
                        # add testing to see if regexes are overlappingc


        except Exception as e:
            # time_exceeded_count += 1
            print("ERROR!")
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            # exit()
            TimeExceeded = True
            print('time limit exceded')
        # NoFailDetected = not (BuildError or TestFail or TestError or CodeAnalysisError or TravisError or DeploymentError)
        # print(str(file_name) + ' processed')

        # list_found = list(unique_everseen(list_found))
        return [file_name, ml_found_around_list]
        # csv_res.write('\n')

    def process_file_with_regexes_test_error(self):
        file_name = self.file
        print('processing ' + file_name)
        file = open(os.path.join('', file_name),
                    encoding='utf-8')  # C:\Users\dhiarzig\PycharmProjects\ML-CI\Project Stats Year
        contents = file.read()
        lines = contents.split('\n')
        ml_found_around_list = []
        try:
            with time_limit(61):
                CAScanningMode = False
                TestScanningMode = False
                lines_tups_list = []
                for i in range(0, len(lines)):
                    line = lines[i]
                    test_command_regex_0 = r"0K\$ (?!pip)\b.* [A-Za-z]*test"
                    test_command_regex_1 = r"0K\$ (?!pip)\b.* nose"
                    test_command_regex_2 = r"0K\$ [A-Za-z]*sh ([^ !$`&*()+]|(\\[ !$`&*()+]))+([a-zA-Z0-9\s_\\.\-\(\):])*test([a-zA-Z0-9\s_\\.\-\(\):])*.sh"
                    test_command_regex_3 = r"0K\$ python (-|--)?[A-za-z]* unittest"

                    test_command_regex_5 = r"0K\$.* (?!pip)\b[A-Za-z]*test"
                    pattern0 = regex.compile(test_command_regex_0)
                    pattern1 = regex.compile(test_command_regex_1)
                    pattern2 = regex.compile(test_command_regex_2)
                    pattern3 = regex.compile(test_command_regex_3)

                    pattern5 = regex.compile(test_command_regex_5)
                    if ("==== test session starts ===" in line) or ("flask test" in line) or (
                            pattern0.search(line)) or (pattern1.search(line)) or (pattern2.search(line)) or (
                            pattern3.search(line)) or (pattern5.search(line)):  # (pattern4.search(line))

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

                    for tup in regexes_testerror_list:
                        str_regex = tup[0]
                        sub_type = tup[1]
                        if (str_regex[1] == '"' and str_regex[-1] == '"'):
                            str_regex = str_regex[1:-1]
                        str_regex = str_regex.replace('""', '"')
                        pattern = regex.compile(str_regex)
                        if pattern.search(line):

                            lines_around = collect_lines(i, lines)
                            lines_tups_list.append(lines_around)
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
                                lines_around = collect_lines(i, lines)
                                lines_tups_list.append(lines_around)
                                break

                for i in range(0, len(lines_tups_list)):
                    tup = lines_tups_list[i]
                    for line in tup:
                        for str_regex in regexes_ml_list:
                            if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                str_regex = str_regex[1:-1]
                            # print(str_regex)
                            pattern = regex.compile(str_regex)
                            if pattern.search(line):
                                # TestFail = True
                                ml_found_around_list.append(tup)
                                i = i + 1
                        # add testing to see if regexes are overlappingc


        except Exception as e:
            # time_exceeded_count += 1
            print("ERROR!")
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            # exit()
            TimeExceeded = True
            print('time limit exceded')
        # NoFailDetected = not (BuildError or TestFail or TestError or CodeAnalysisError or TravisError or DeploymentError)
        # print(str(file_name) + ' processed')

        # list_found = list(unique_everseen(list_found))
        return [file_name, ml_found_around_list]
        # csv_res.write('\n')

    def process_file_with_regexes_fail_ml_all(self):
        file_name=self.file
        print('processing ' + file_name)
        file = open(os.path.join('', file_name), encoding='utf-8') #C:\Users\dhiarzig\PycharmProjects\ML-CI\Project Stats Year
        contents = file.read()
        lines= contents.split('\n')
        try:
            with time_limit(61):
                ml_found_around_list=[]
                # print('tups')
                # print(len(lines_tups_list))
                for i in range(0,len(lines)):
                    line=lines[i]
                    for str_regex in regexes_ml_list:
                        if (str_regex[1] == '"' and str_regex[-1] == '"'):
                            str_regex = str_regex[1:-1]
                        # print(str_regex)
                        pattern = regex.compile(str_regex)
                        if pattern.search(line):
                            # TestFail = True
                            ml_found_around_list.append(collect_lines(i,lines))
                            i=i+1
                # print('ml tups')
                # print(len(ml_found_around_list))

                        # add testing to see if regexes are overlappingc
        except Exception as e:
            print("ERROR!")
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print('time limit exceded')
        return [self.file,ml_found_around_list]


    # def my_process(self, multiply_by, add_to):
    #     self.result = self.input * multiply_by
    #     self._my_sub_process(add_to)
    #     return self.result
    #
    # def _my_sub_process(self, add_to):
    #     self.result += add_to


NUM_CORE = 8

def worker(arg):
    obj= arg
    return obj.process_file_with_regexes()

if __name__ == "__main__":
    start_time_all = time.perf_counter()
    all_job_logs = [y for x in os.walk('C:\\Users\\dhiarzig\\PycharmProjects\\ML-CI\\Project Stats Year') for y in
                    glob(os.path.join(x[0], '*.txt'))]
    # all_job_csv = [y for x in os.walk('C:\\Users\\dhiarzig\\PycharmProjects\\ML-CI\\Project Stats Year') for y in
    #                glob(os.path.join(x[0], 'job_detailed_info.csv'))]
    # for job_csv in all_job_csv:
    #     try:
    df_csv = pd.read_csv('../../CSV Outputs/classification_all_08_03_2021.csv')
    test_failed_jobs = df_csv[df_csv['TestFail'] == True]['file_name'].to_list()
    # print(test_failed_jobs[:10])
    # # test_failed_jobs = [str(x).split('\\')[-1] for x in test_failed_jobs]
    # job_failed_logs = test_failed_jobs
    # # print(job_failed_logs[:10])
    # # file=open('C:\\Users\\dhiarzig\\PycharmProjects\\ML-CI\\CSV Outputs\\3liners_08_03_2021_testfail.txt','r',encoding='utf-8')
    # # print('3liners_testfail.txt')
    # # lines=file.read().split('===============C:\\Users\\dhiarzig\\PycharmProjects\\ML-CI\\Project Stats Year\\')
    # list_of_objects = [Log_failure_classifier(i,'fail') for i in job_failed_logs]
    # pool = mp.Pool(NUM_CORE)
    # tup_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    # pool.close()
    # pool.join()
    # # print(tup_of_results)
    # csv_res_testfail = open('../../CSV Outputs/3liners_ml_test_fail_list_08_05_2021.txt', 'w+', encoding='utf-8')
    #
    # for res_line in tup_of_results:
    #     file_name = res_line[0]
    #     ml_lines = res_line[1]
    #     if (len(ml_lines) > 0):
    #         csv_res_testfail.write("===============" + str(file_name) + "================")
    #         csv_res_testfail.write('\n')
    #         for tup in ml_lines:
    #             for line in tup:
    #                 try:
    #                     print(str(line))
    #                     csv_res_testfail.write(str(line))
    #                     csv_res_testfail.write('\n')
    #
    #                 except:
    #                     continue
    # csv_res_testfail.flush()
    #
    # test_failed_jobs = df_csv[df_csv['TestError'] == True]['file_name'].to_list()
    # print(test_failed_jobs[:10])
    # # test_failed_jobs = [str(x).split('\\')[-1] for x in test_failed_jobs]
    # job_failed_logs = test_failed_jobs
    # # print(job_failed_logs[:10])
    # # file=open('C:\\Users\\dhiarzig\\PycharmProjects\\ML-CI\\CSV Outputs\\3liners_08_03_2021_testfail.txt','r',encoding='utf-8')
    # # print('3liners_testfail.txt')
    # # lines=file.read().split('===============C:\\Users\\dhiarzig\\PycharmProjects\\ML-CI\\Project Stats Year\\')
    # list_of_objects = [Log_failure_classifier(i, 'test_error') for i in job_failed_logs]
    # pool = mp.Pool(NUM_CORE)
    # tup_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    # pool.close()
    # pool.join()
    # # print(tup_of_results)
    # csv_res_testerror = open('../../CSV Outputs/3liners_ml_test_error_list_08_05_2021.txt', 'w+', encoding='utf-8')
    # for res_line in tup_of_results:
    #     file_name = res_line[0]
    #     ml_lines = res_line[1]
    #     if (len(ml_lines) > 0):
    #         csv_res_testerror.write("===============" + str(file_name) + "================")
    #         csv_res_testerror.write('\n')
    #         for tup in ml_lines:
    #             for line in tup:
    #                 try:
    #                     print(str(line))
    #                     csv_res_testerror.write(str(line))
    #                     csv_res_testerror.write('\n')
    #
    #                 except:
    #                     continue
    # csv_res_testerror.flush()
    #
    # test_failed_jobs = df_csv[df_csv['BuildError'] == True]['file_name'].to_list()
    # print(test_failed_jobs[:10])
    # # test_failed_jobs = [str(x).split('\\')[-1] for x in test_failed_jobs]
    # job_failed_logs = test_failed_jobs
    # print(job_failed_logs[:10])
    # file=open('C:\\Users\\dhiarzig\\PycharmProjects\\ML-CI\\CSV Outputs\\3liners_08_03_2021_testfail.txt','r',encoding='utf-8')
    # print('3liners_testfail.txt')
    # lines=file.read().split('===============C:\\Users\\dhiarzig\\PycharmProjects\\ML-CI\\Project Stats Year\\')
    # list_of_objects = [Log_failure_classifier(i, 'build_error') for i in job_failed_logs]
    # pool = mp.Pool(NUM_CORE)
    # tup_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    # pool.close()
    # pool.join()
    # # print(tup_of_results)
    # csv_res_builderror = open('../../CSV Outputs/3liners_ml_build_error_list_08_05_2021.txt', 'w+', encoding='utf-8')
    # for res_line in tup_of_results:
    #     file_name = res_line[0]
    #     ml_lines = res_line[1]
    #     if (len(ml_lines) > 0):
    #         csv_res_builderror.write("===============" + str(file_name) + "================")
    #         csv_res_builderror.write('\n')
    #         for tup in ml_lines:
    #             for line in tup:
    #                 try:
    #                     print(str(line))
    #                     csv_res_builderror.write(str(line))
    #                     csv_res_builderror.write('\n')
    #
    #                 except:
    #                     continue
    # csv_res_builderror.flush()

    list_of_objects = [Log_failure_classifier(i, 'ml_fail') for i in test_failed_jobs]
    pool = mp.Pool(NUM_CORE)
    tup_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()
    # print(tup_of_results)
    csv_res_testfail = open('../../CSV Outputs/3liners_ml_test_fail_list_whole_file_08_05_2021.txt', 'w+', encoding='utf-8')

    for res_line in tup_of_results:
        file_name = res_line[0]
        ml_lines = res_line[1]
        if (len(ml_lines) > 0):
            csv_res_testfail.write("===============" + str(file_name) + "================")
            csv_res_testfail.write('\n')
            for tup in ml_lines:
                for line in tup:
                    try:
                        print(str(line))
                        csv_res_testfail.write(str(line))
                        csv_res_testfail.write('\n')

                    except:
                        continue
    csv_res_testfail.flush()
    exit()

    # test_failed_jobs = df_csv[df_csv['ml_fail'] == True]['file_name'].to_list()
    # print(test_failed_jobs[:10])
    # test_failed_jobs = [str(x).split('\\')[-1] for x in test_failed_jobs]
    # job_failed_logs = test_failed_jobs
    # print(job_failed_logs[:10])
    # file=open('C:\\Users\\dhiarzig\\PycharmProjects\\ML-CI\\CSV Outputs\\3liners_08_03_2021_testfail.txt','r',encoding='utf-8')
    # print('3liners_testfail.txt')
    # lines=file.read().split('===============C:\\Users\\dhiarzig\\PycharmProjects\\ML-CI\\Project Stats Year\\')
    test_error_jobs = df_csv[df_csv['TestError'] == True]['file_name'].to_list()
    list_of_objects = [Log_failure_classifier(i, 'ml_fail') for i in test_error_jobs]
    pool = mp.Pool(NUM_CORE)
    tup_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()
    # print(tup_of_results)
    csv_res_testerror = open('../../CSV Outputs/3liners_ml_test_error_list_whole_file_08_05_2021.txt', 'w+', encoding='utf-8')
    for res_line in tup_of_results:
        file_name = res_line[0]
        ml_lines = res_line[1]
        if (len(ml_lines) > 0):
            csv_res_testerror.write("===============" + str(file_name) + "================")
            csv_res_testerror.write('\n')
            for tup in ml_lines:
                for line in tup:
                    try:
                        print(str(line))
                        csv_res_testerror.write(str(line))
                        csv_res_testerror.write('\n')

                    except:
                        continue
    csv_res_testerror.flush()


    # print(test_failed_jobs[:10])
    # test_failed_jobs = [str(x).split('\\')[-1] for x in test_failed_jobs]
    # job_failed_logs = test_failed_jobs
    # print(job_failed_logs[:10])
    # file=open('C:\\Users\\dhiarzig\\PycharmProjects\\ML-CI\\CSV Outputs\\3liners_08_03_2021_testfail.txt','r',encoding='utf-8')
    # print('3liners_testfail.txt')
    # lines=file.read().split('===============C:\\Users\\dhiarzig\\PycharmProjects\\ML-CI\\Project Stats Year\\')

    build_error_jobs = df_csv[df_csv['BuildError'] == True]['file_name'].to_list()
    list_of_objects = [Log_failure_classifier(i, 'ml_fail') for i in build_error_jobs]
    pool = mp.Pool(NUM_CORE)
    tup_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()
    # print(tup_of_results)
    csv_res_builderror = open('../../CSV Outputs/3liners_ml_build_error_list_whole_file_08_05_2021.txt', 'w+', encoding='utf-8')
    for res_line in tup_of_results:
        file_name = res_line[0]
        ml_lines = res_line[1]
        if (len(ml_lines) > 0):
            csv_res_builderror.write("===============" + str(file_name) + "================")
            csv_res_builderror.write('\n')
            for tup in ml_lines:
                for line in tup:
                    try:
                        print(str(line))
                        csv_res_builderror.write(str(line))
                        csv_res_builderror.write('\n')

                    except:
                        continue
    csv_res_builderror.flush()

    # exit()
    # # list_of_results = []
    # # for tup in tup_of_results:
    # #     list_of_results.extend(tup[1])
    # # a=dict()
    # # for el in list_of_results:
    # #     if el[0] in a.keys():
    # #         a[el[0]].append(el[1])
    # #     else:
    # #         a[el[0]] = [el[1]]
    # # pprint(a)
    # # json_content = json.dumps(a)
    # # f = open("3liners_testfail_ml_term.json", "w")
    # # f.write(json_content)
    # # f.close()
    #
    # file = open('C:\\Users\\dhiarzig\\PycharmProjects\\ML-CI\\CSV Outputs\\3liners_08_03_2021_testerror.txt', 'r', encoding='utf-8')
    # print('testerror.txt')
    # lines = file.readlines()
    # list_of_objects = [Log_failure_classifier(i) for i in lines]
    # pool = mp.Pool(NUM_CORE)
    # tup_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    # pool.close()
    # pool.join()
    # list_of_results = []
    # for tup in tup_of_results:
    #     list_of_results.extend(tup[1])
    #
    # # a = dict((letter, list_of_results.count(letter)) for letter in set(list_of_results))
    #
    # a = dict()
    # for el in list_of_results:
    #     if el[0] in a.keys():
    #         a[el[0]].append(el[1])
    #     else:
    #         a[el[0]] = [el[1]]
    # pprint(a)
    # json_content = json.dumps(a)
    # f = open("3liners_testerror_ml_term.json", "w")
    # f.write(json_content)
    # f.close()
    #
    # file = open('C:\\Users\\dhiarzig\\PycharmProjects\\ML-CI\\CSV Outputs\\3liners_08_03_2021_caerror.txt', 'r', encoding='utf-8')
    # print('3liners_caerror.txt')
    # lines = file.readlines()
    # list_of_objects = [Log_failure_classifier(i) for i in lines]
    # pool = mp.Pool(NUM_CORE)
    # tup_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    # pool.close()
    # pool.join()
    # list_of_results = []
    # for tup in tup_of_results:
    #     list_of_results.extend(tup[1])
    #
    # # a = dict((letter, list_of_results.count(letter)) for letter in set(list_of_results))
    # a = dict()
    # for el in list_of_results:
    #     if el[0] in a.keys():
    #         a[el[0]].append(el[1])
    #     else:
    #         a[el[0]] = [el[1]]
    # pprint(a)
    # pprint(a)
    # json_content = json.dumps(a)
    # f = open("3liners_caerror_ml_term.json", "w")
    # f.write(json_content)
    # f.close()
    #
    # file = open('C:\\Users\\dhiarzig\\PycharmProjects\\ML-CI\\CSV Outputs\\3liners_08_03_2021_scripterror.txt', 'r', encoding='utf-8')
    # print('scripterror.txt')
    # lines = file.readlines()
    # list_of_objects = [Log_failure_classifier(i) for i in lines]
    # pool = mp.Pool(NUM_CORE)
    # tup_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    # pool.close()
    # pool.join()
    # list_of_results = []
    # for tup in tup_of_results:
    #     list_of_results.extend(tup[1])
    # # a = dict((letter, list_of_results.count(letter)) for letter in set(list_of_results))
    # a = dict()
    # for el in list_of_results:
    #     if el[0] in a.keys():
    #         a[el[0]].append(el[1])
    #     else:
    #         a[el[0]] = [el[1]]
    # # pprint(a)
    # # pprint(a)
    # json_content = json.dumps(a)
    # f = open("3liners_scripterror_ml_term.json", "w")
    # f.write(json_content)
    # f.close()
    #
    # file = open('C:\\Users\\dhiarzig\\PycharmProjects\\ML-CI\\CSV Outputs\\3liners_08_03_2021_deploymenterror.txt', 'r', encoding='utf-8')
    # print('3liners_deploymenterror.txt')
    # lines = file.readlines()
    # list_of_objects = [Log_failure_classifier(i) for i in lines]
    # pool = mp.Pool(NUM_CORE)
    # tup_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    # pool.close()
    # pool.join()
    # list_of_results = []
    # for tup in tup_of_results:
    #     list_of_results.extend(tup[1])
    # # a = dict((letter, list_of_results.count(letter)) for letter in set(list_of_results))
    # a = dict()
    # for el in list_of_results:
    #     if el[0] in a.keys():
    #         a[el[0]].append(el[1])
    #     else:
    #         a[el[0]] = [el[1]]
    # pprint(a)
    # json_content = json.dumps(a)
    # f = open("3liners_deploymenterror_ml_term.json", "w")
    # f.write(json_content)
    # f.close()


    end_time_all = time.perf_counter()
    print(f"Execution Time : {end_time_all - start_time_all:0.6f}")


