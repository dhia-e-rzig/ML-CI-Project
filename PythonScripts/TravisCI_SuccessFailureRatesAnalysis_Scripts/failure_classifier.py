import pandas as pd
import regex
import os
import time
import _thread
import threading
from contextlib import contextmanager

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

regexes_csv=pd.read_csv('../../CSV Inputs/all_regexes_v1.csv')

regexes_testfail_list=regexes_csv.loc[regexes_csv['Failure Type'] == 'Test Fail']['Regex'].to_list()
# print(len(regexes_testfail_list))
regexes_buildfail_list=regexes_csv.loc[regexes_csv['Failure Type'] == 'Build Error']['Regex'].to_list()
# print(len(regexes_buildfail_list))
regexes_testerror_list=regexes_csv.loc[regexes_csv['Failure Type'] == 'Test Error']['Regex'].to_list()
# print(len(regexes_testerror_list))
regexes_cafail_list=regexes_csv.loc[regexes_csv['Failure Type'] == 'Code Analysis Error']['Regex'].to_list()
# print(len(regexes_cafail_list))
regexes_travisfail_list=regexes_csv.loc[regexes_csv['Failure Type'] == 'Travis Error']['Regex'].to_list()
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
        f=self.file
        TimeExceeded=False
        NotPythonLang=False
        NoFailDetected = True
        pyflakes_mode = False
        TestFail = False
        BuildFail = False
        TestError = False
        CodeAnalysisError = False
        TravisError=False
        print('processing ' + f)
        file = open(os.path.join('../../FailedLogs-ForDetectionTesting', f), encoding='utf-8')
        try:
            with time_limit(61):
                for line in file:
                   list_test_fail_regexes_found=[]
                   list_test_error_regexes_found=[]
                   list_build_fail_regexes_found=[]
                   list_ca_fail_regexes_found=[]
                   list_travis_fail_regexes_found=[]
                   if TestFail and BuildFail and TestError and CodeAnalysisError and TravisError:
                        break
                   if ('Build language') in line and not (('python') in line or ('generic') in line):
                        print('build language is not python')
                        # lang_not_python_count += 1
                        # print('lang not python')
                        NotPythonLang=True
                        break
                   if not TestFail:
                        for str_regex in regexes_testfail_list:
                            if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                str_regex = str_regex[1:-1]
                            # print(str_regex)
                            pattern = regex.compile(str_regex)
                            if pattern.search(line):
                                TestFail = True
                                list_travis_fail_regexes_found.append(str_regex)
                            # add testing to see if regexes are overlapping
                   if not BuildFail:
                        for str_regex in regexes_buildfail_list:
                            if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                str_regex = str_regex[1:-1]
                            pattern = regex.compile(str_regex)
                            if pattern.search(line):
                                BuildFail = True
                                list_build_fail_regexes_found.append(str_regex)

                   if not TestError:
                        for str_regex in regexes_testerror_list:
                            if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                str_regex = str_regex[1:-1]
                            pattern = regex.compile(str_regex)
                            if pattern.search(line):
                                TestError = True
                                list_test_error_regexes_found.append(str_regex)
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
                                if pattern.search(line):
                                    CodeAnalysisError = True
                                    list_ca_fail_regexes_found.append(str_regex)

                   if not TravisError:
                        for str_regex in regexes_travisfail_list:
                            if(str_regex[1] == '"' and str_regex[-1] =='"'):
                                str_regex=str_regex[1:-1]
                            pattern = regex.compile(str_regex)
                            if pattern.search(line):
                                TravisError = True
                                list_travis_fail_regexes_found.append(str_regex)
                   if (len(list_test_fail_regexes_found)>1):
                        with open('regex_together_test_fail.csv','a+',encoding='utf-8') as f:
                            f.write(str(list_test_fail_regexes_found))
                            f.write('\n')
                   if (len(list_test_error_regexes_found)>1):
                       with open('regex_together_test_error.csv','a+',encoding='utf-8') as f:
                           f.write(str(list_test_error_regexes_found))
                           f.write('\n')
                   if (len(list_build_fail_regexes_found)>1):
                       with open('regex_together_build_fail.csv','a+',encoding='utf-8') as f:
                            f.write(str(list_build_fail_regexes_found))
                            f.write('\n')
                   if (len(list_ca_fail_regexes_found) > 1):
                       with open('regex_together_ca_error.csv', 'a+', encoding='utf-8') as f:
                           f.write(str(list_ca_fail_regexes_found))
                           f.write('\n')
                   if (len(list_test_error_regexes_found) > 1):
                       with open('regex_together_travis_error.csv', 'a+', encoding='utf-8') as f:
                           f.write(str(list_test_error_regexes_found))
                           f.write('\n')
        except Exception as e:
            # time_exceeded_count += 1
            print(e)
            # exit()
            TimeExceeded=True
            print('time limit exceded for file: ' + f)
        NoFailDetected = not (BuildFail or TestFail or TestError or CodeAnalysisError or TravisError)
        print(str(f) + ' processed')
        return str(str(f) + ',' + str(TestFail) + ',' + str(BuildFail) + ',' + str(TestError) + ',' + str(
            CodeAnalysisError)+ ',' +str(TravisError) + ',' + str(NoFailDetected)+','+str(TimeExceeded)+','+str(NotPythonLang))
        # csv_res.write('\n')


    # def my_process(self, multiply_by, add_to):
    #     self.result = self.input * multiply_by
    #     self._my_sub_process(add_to)
    #     return self.result
    #
    # def _my_sub_process(self, add_to):
    #     self.result += add_to

import multiprocessing as mp
NUM_CORE = 8

def worker(arg):
    obj= arg
    return obj.process_file_with_regexes()

if __name__ == "__main__":
    start_time_all = time.perf_counter()
    log_files = os.listdir('../../FailedLogs-ForDetectionTesting')
    list_of_objects = [Log_failure_classifier(i) for i in log_files]
    pool = mp.Pool(NUM_CORE)
    list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()

    csv_res = open('../../CSV Inputs/csv_for_eval_fail/detection_eval/classification_test_v1_regex.csv', 'w+')
    csv_res.write('file_name,TestFail,BuildFail,TestError,CodeAnalysisError,TravisError,NoFailDetected,TimeExceeded,NotPythonLang')
    csv_res.write('\n')
    for line in list_of_results:
        csv_res.write(line)
        csv_res.write('\n')
    end_time_all = time.perf_counter()
    print(f"Execution Time : {end_time_all - start_time_all:0.6f}")


