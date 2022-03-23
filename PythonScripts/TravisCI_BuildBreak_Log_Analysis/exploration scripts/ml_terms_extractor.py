import re

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

regexes_csv=pd.read_csv('../../CSV Inputs/regex_ml_curated.csv')

regexes_ml_list=regexes_csv.loc[regexes_csv['Type'] == 'ML']['Regex'].to_list()
# # print(len(regexes_testfail_list))
# regexes_buildfail_list=regexes_csv.loc[regexes_csv['Failure Type'] == 'Build Error']['Regex'].to_list()
# # print(len(regexes_buildfail_list))
# regexes_testerror_list=regexes_csv.loc[regexes_csv['Failure Type'] == 'Test Error']['Regex'].to_list()
# # print(len(regexes_testerror_list))
# regexes_cafail_list=regexes_csv.loc[regexes_csv['Failure Type'] == 'Code Analysis Error']['Regex'].to_list()
# # print(len(regexes_cafail_list))
# regexes_travisfail_list=regexes_csv.loc[regexes_csv['Failure Type'] == 'Travis Error']['Regex'].to_list()
#
# regexes_deploymenterror_list=regexes_csv.loc[regexes_csv['Failure Type'] == 'Deployment Error']['Regex'].to_list()

regexes_csv.fillna(inplace=True,value="0")
# regexes_testfail_addition_list=regexes_csv.loc[regexes_csv['Notes'].str.contains('can be test fail')]['Regex'].to_list()
# regexes_testerror_addition_list=regexes_csv.loc[regexes_csv['Notes'].str.contains('can be test error')]['Regex'].to_list()


# print(len(regexes_travisfail_list))

# pprint(log_files)
# exit()



# pyflakes_mode=False
# TestFail=False
# BuildFail=False
# TestError=False
# CodeAnalysisError=False

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
    def __init__(self, file):
        self.file = file
        self.result = ""
    def process_file_with_regexes(self):
        file_name=self.file
        TimeExceeded=False
        NotPythonLang=False
        NoFailDetected = True
        pyflakes_mode = False
        TestFail = False
        BuildError = False
        TestError = False
        CodeAnalysisError = False
        DeploymentError = False
        TravisError=True # testing for incomplete files
        print('processing ' + file_name)
        file = open(os.path.join('', file_name), encoding='utf-8') #C:\Users\dhiarzig\PycharmProjects\ML-CI\Project Stats Year
        contents = file.read()
        lines= contents.split('\n')
        try:
            with time_limit(61):
                list_found = []
                for i in range(0,len(lines)):
                   line=lines[i]
                   for str_regex in regexes_ml_list:
                       if (str_regex[1] == '"' and str_regex[-1] == '"'):
                           str_regex = str_regex[1:-1]
                       # print(str_regex)
                       pattern = regex.compile(str_regex)
                       if pattern.search(line):
                           # TestFail = True
                           list_found.append(collect_lines(i,lines))
                            # add testing to see if regexes are overlapping

        except Exception as e:
            # time_exceeded_count += 1
            print("ERROR!")
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            # exit()
            TimeExceeded=True
            print('time limit exceded for file: ' + file_name)
        # NoFailDetected = not (BuildError or TestFail or TestError or CodeAnalysisError or TravisError or DeploymentError)
        print(str(file_name) + ' processed')

        list_found = list(unique_everseen(list_found))
        return [str(file_name) ,list_found]
        # csv_res.write('\n')


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
    result = [y for x in os.walk('C:\\Users\\dhiarzig\\PycharmProjects\\ML-CI\\Project Stats Year') for y in glob(os.path.join(x[0], '*.txt'))]
    log_files = result
    splits = np.array_split(result, 50)
    i=0
    for log_files in splits:
        list_of_objects = [Log_failure_classifier(i) for i in log_files]
        pool = mp.Pool(NUM_CORE)
        list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
        pool.close()
        pool.join()
        # return [str(file_name), list_test_fail_lines_found,
        #         list_build_error_lines_found, list_test_error_lines_found, list_ca_fail_lines_found,
        #         list_travis_fail_lines_found, list_deployment_error_lines_found]
        csv_res_testfail = open('../../CSV Outputs/3liners_ml.txt', 'a+',encoding='utf-8')
        # csv_res_scripterror = open('../../CSV Outputs/3liners_scripterror.txt', 'w+',encoding='utf-8')
        # csv_res_testerror = open('../../CSV Outputs/3liners_testerror.txt', 'w+',encoding='utf-8')
        # csv_res_caerror = open('../../CSV Outputs/3liners_caerror.txt', 'w+',encoding='utf-8')
        # csv_res_deploymenterror = open('../../CSV Outputs/3liners_deploymenterror.txt', 'w+',encoding='utf-8')
        # csv_res_traviserror = open('../../CSV Outputs/3liners_traviserror.txt', 'w+',encoding='utf-8')
        # csv_res.write('file_name,TestFail,BuildError,TestError,CodeAnalysisError,TravisError,DeploymentError,NoFailDetected,TimeExceeded,NotPythonLang')
        # csv_res.write('\n')

        for res_line in list_of_results:
            file_name=res_line[0]
            ml_lines=res_line[1]
            if(len(ml_lines) > 0):
                csv_res_testfail.write("==============="+str(file_name)+"================")
                csv_res_testfail.write('\n')
                for tup in ml_lines:
                    for line in tup:
                        try:
                            csv_res_testfail.write(str(line))
                            csv_res_testfail.write('\n')
                        except:
                            continue
        i+=1
        try:
           progress_text = open('../../CSV Outputs/ml_list_finished.txt', 'w+', encoding='utf-8')
           progress_text.write('ListFinished:'+str(i))
        except:
           print(i)

    end_time_all = time.perf_counter()
    print(f"Execution Time : {end_time_all - start_time_all:0.6f}")


