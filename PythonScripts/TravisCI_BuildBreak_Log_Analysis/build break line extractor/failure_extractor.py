import re

import pandas as pd
import regex
import os
import time
import _thread
import threading
from contextlib import contextmanager
from glob import glob

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

regexes_csv=pd.read_csv('../../CSV Inputs/regex_failure.csv')

regexes_testfail_list=regexes_csv.loc[regexes_csv['Failure Type'] == 'Test Fail']['Regex'].to_list()
# print(len(regexes_testfail_list))
regexes_buildfail_list=regexes_csv.loc[regexes_csv['Failure Type'] == 'Build Error']['Regex'].to_list()
# print(len(regexes_buildfail_list))
regexes_testerror_list=regexes_csv.loc[regexes_csv['Failure Type'] == 'Test Error']['Regex'].to_list()
# print(len(regexes_testerror_list))
regexes_cafail_list=regexes_csv.loc[regexes_csv['Failure Type'] == 'Code Analysis Error']['Regex'].to_list()
# print(len(regexes_cafail_list))
regexes_travisfail_list=regexes_csv.loc[regexes_csv['Failure Type'] == 'Travis Error']['Regex'].to_list()

regexes_deploymenterror_list=regexes_csv.loc[regexes_csv['Failure Type'] == 'Deployment Error']['Regex'].to_list()

regexes_csv.fillna(inplace=True,value="0")
regexes_testfail_addition_list=regexes_csv.loc[regexes_csv['Notes'].str.contains('can be test fail')]['Regex'].to_list()
regexes_testerror_addition_list=regexes_csv.loc[regexes_csv['Notes'].str.contains('can be test error')]['Regex'].to_list()


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
        line_2 = lines[i +1]
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
        if line_2.strip() =="":
            line_2=line_1
            line_1=line_0
            line_0= lines[i - 2]
            j=i-2
            while clean_line(line_0.strip()) == "" and j > 1:
                j = j - 1
                line_0 = lines[j]

        return(line_0,line_1,line_2)

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
                TestScanningMode=False
                CAScanningMode=False
                IgnoreMode=False
                list_test_fail_lines_found = []
                list_test_error_lines_found = []
                list_build_error_lines_found = []
                list_ca_fail_lines_found = []
                list_travis_fail_lines_found = []
                list_deployment_error_lines_found = []

                for i in range(0,len(lines)):
                   line=lines[i]
                   # exec_patt_1=regex.compile("====== <exec> ======")
                   # exec_patt_2=regex.compile("====== </exec> ======")
                   # if exec_patt_1.search(line):
                   #     IgnoreMode=True
                   # if exec_patt_2.search(line):
                   #     IgnoreMode=False
                   # if IgnoreMode:
                   #    continue
                   patt_str=r"=+ FAILURES =+"
                   patt=re.compile(patt_str)
                   if TestFail and len(list_test_fail_lines_found) == 1 and patt.search(list_test_fail_lines_found[0][1]) and "FLAKE8" in line:
                       # print("FLAKEREM")
                       TestFail=False
                       list_test_fail_lines_found.clear()

                   if "Done. Your build exited with" in line: # testing for incomplete files
                       TravisError=False
                   # if TestFail and BuildError and TestError and CodeAnalysisError and TravisError and DeploymentError:
                   #     return [str(file_name) ,list_test_fail_lines_found,
                   #                 list_build_error_lines_found,list_test_error_lines_found,list_ca_fail_lines_found ,list_travis_fail_lines_found,list_deployment_error_lines_found]
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
                   if("==== test session starts ===" in line )or("flask test"in line)or(pattern0.search(line))or (pattern1.search(line)) or (pattern2.search(line)) or (pattern3.search(line)) or(pattern5.search(line)):#(pattern4.search(line))
                       # if(file_name=="152299145.txt"):
                       #     print(pattern1.search(line))
                       #     print(pattern2.search(line))
                       #     print(pattern3.search(line))
                       #     print(pattern4.search(line))
                       #     print(pattern5.search(line))
                       #     print(line)
                       #     exit()
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
                       TestScanningMode=False
                   if("The command " in line) or ("travis_time:end:" in line):
                       CAScanningMode=False
                   # if ('Build language') in line and not (('python') in line or ('generic') in line):
                   #      print('build language is not python')
                   #      # lang_not_python_count += 1
                   #      # print('lang not python')
                   #      NotPythonLang=True
                   #      break
                   # if not TestFail:
                   for str_regex in regexes_testfail_list:
                       if (str_regex[1] == '"' and str_regex[-1] == '"'):
                           str_regex = str_regex[1:-1]
                       # print(str_regex)
                       pattern = regex.compile(str_regex)
                       if pattern.search(line):
                           TestFail = True
                           list_test_fail_lines_found.append(collect_lines(i,lines))
                            # add testing to see if regexes are overlapping
                   if TestScanningMode:
                       for str_regex in regexes_testfail_addition_list:
                           if (str_regex[1] == '"' and str_regex[-1] == '"'):
                               str_regex = str_regex[1:-1]
                           pattern = regex.compile(str_regex)
                           if pattern.search(line):
                               TestFail = True
                               list_test_fail_lines_found.append(collect_lines(i,lines))

                   # if not BuildError:
                   regex_list=regexes_buildfail_list
                   if TestScanningMode or CAScanningMode:
                       regex_list =[] #[i for i in regexes_buildfail_list if i not in regexes_testfail_addition_list]
                   for str_regex in regex_list:
                       if (str_regex[1] == '"' and str_regex[-1] == '"'):
                           str_regex = str_regex[1:-1]
                       pattern = regex.compile(str_regex)
                       if pattern.search(line):
                           BuildError = True
                           list_build_error_lines_found.append(collect_lines(i,lines))

                   # if not TestError:
                   for str_regex in regexes_testerror_list:
                       if (str_regex[1] == '"' and str_regex[-1] == '"'):
                           str_regex = str_regex[1:-1]
                       pattern = regex.compile(str_regex)
                       if pattern.search(line):
                           TestError = True
                           list_test_error_lines_found.append(collect_lines(i,lines))
                   if TestScanningMode:
                       for str_regex in regexes_testerror_addition_list:
                           if (str_regex[1] == '"' and str_regex[-1] == '"'):
                               str_regex = str_regex[1:-1]
                           pattern = regex.compile(str_regex)
                           if pattern.search(line):
                               TestFail = True
                               list_test_error_lines_found.append(collect_lines(i,lines))


                   # if not CodeAnalysisError:
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
                               list_ca_fail_lines_found.append(collect_lines(i,lines))
                       else:
                           if (str_regex[1] == '"' and str_regex[-1] == '"'):
                               str_regex = str_regex[1:-1]
                           pattern = regex.compile(str_regex)
                           if pattern.search(line):
                               CodeAnalysisError = True
                               list_ca_fail_lines_found.append(collect_lines(i,lines))
                       if CAScanningMode:
                           for str_regex in regexes_testfail_addition_list:
                               if (str_regex[1] == '"' and str_regex[-1] == '"'):
                                   str_regex = str_regex[1:-1]
                               pattern = regex.compile(str_regex)
                               if pattern.search(line):
                                   CodeAnalysisError = True
                                   list_ca_fail_lines_found.append(collect_lines(i,lines))


                   # if not TravisError:
                   for str_regex in regexes_travisfail_list:
                       if(str_regex[1] == '"' and str_regex[-1] =='"'):
                           str_regex=str_regex[1:-1]
                       pattern = regex.compile(str_regex)
                       if pattern.search(line):
                           TravisError = True
                           list_travis_fail_lines_found.append(collect_lines(i,lines))

                   # if not DeploymentError:
                   for str_regex in regexes_deploymenterror_list:
                       if(str_regex[1] == '"' and str_regex[-1] =='"'):
                           str_regex=str_regex[1:-1]
                       pattern = regex.compile(str_regex)
                       if pattern.search(line):
                           TravisError = True
                           tups=collect_lines(i,lines)
                           print('TUPS')
                           print(tups)
                           list_deployment_error_lines_found.append(tups)
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
            print("ERROR!")
            print(e)
            # exit()
            TimeExceeded=True
            print('time limit exceded for file: ' + file_name)
        NoFailDetected = not (BuildError or TestFail or TestError or CodeAnalysisError or TravisError or DeploymentError)
        print(str(file_name) + ' processed')
        from more_itertools import unique_everseen
        list_test_fail_lines_found = list(unique_everseen(list_test_fail_lines_found))
        list_build_error_lines_found = list(unique_everseen(list_build_error_lines_found))
        list_test_error_lines_found = list(unique_everseen(list_test_error_lines_found))
        list_ca_fail_lines_found = list(unique_everseen(list_ca_fail_lines_found))
        list_travis_fail_lines_found = list(unique_everseen(list_travis_fail_lines_found))
        list_deployment_error_lines_found = list(unique_everseen(list_deployment_error_lines_found))

        return [str(file_name) ,list_test_fail_lines_found,
                                   list_build_error_lines_found,list_test_error_lines_found,list_ca_fail_lines_found ,list_travis_fail_lines_found,list_deployment_error_lines_found]
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
    result = [y for x in os.walk('C:\\Users\\dhiarzig\\PycharmProjects\\ML-CI\\Project Stats Year') for y in glob(os.path.join(x[0], '*.txt'))]
    log_files = result
    list_of_objects = [Log_failure_classifier(i) for i in log_files]
    pool = mp.Pool(NUM_CORE)
    list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()
    # return [str(file_name), list_test_fail_lines_found,
    #         list_build_error_lines_found, list_test_error_lines_found, list_ca_fail_lines_found,
    #         list_travis_fail_lines_found, list_deployment_error_lines_found]
    csv_res_testfail = open('../../CSV Outputs/3liners_testfail.txt', 'w+',encoding='utf-8')
    csv_res_scripterror = open('../../CSV Outputs/3liners_scripterror.txt', 'w+',encoding='utf-8')
    csv_res_testerror = open('../../CSV Outputs/3liners_testerror.txt', 'w+',encoding='utf-8')
    csv_res_caerror = open('../../CSV Outputs/3liners_caerror.txt', 'w+',encoding='utf-8')
    csv_res_deploymenterror = open('../../CSV Outputs/3liners_deploymenterror.txt', 'w+',encoding='utf-8')
    csv_res_traviserror = open('../../CSV Outputs/3liners_traviserror.txt', 'w+',encoding='utf-8')
    # csv_res.write('file_name,TestFail,BuildError,TestError,CodeAnalysisError,TravisError,DeploymentError,NoFailDetected,TimeExceeded,NotPythonLang')
    # csv_res.write('\n')

    for res_line in list_of_results:
        file_name=res_line[0]
        test_fails=res_line[1]
        build_error=res_line[2]
        test_errors=res_line[3]
        ca_fails=res_line[4]
        travis_errors=res_line[5]
        deploy_fails=res_line[6]
        if(len(test_fails) > 0):
            csv_res_testfail.write("==============="+str(file_name)+"================")
            csv_res_testfail.write('\n')
            for tup in test_fails:
                for line in tup:
                    try:
                        csv_res_testfail.write(str(line))
                        csv_res_testfail.write('\n')
                    except:
                        continue
        if (len(build_error) > 0):
            csv_res_scripterror.write("===============" + str(file_name) + "================")
            csv_res_scripterror.write('\n')
            for tup in build_error:
                for line in tup:
                    try:
                        csv_res_scripterror.write(str(line))
                        csv_res_scripterror.write('\n')
                    except:
                        continue
        if (len(test_errors) > 0):
            csv_res_testerror.write("===============" + str(file_name) + "================")
            csv_res_testerror.write('\n')
            for tup in test_errors:
                for line in tup:
                    try:
                        csv_res_testerror.write(str(line))
                        csv_res_testerror.write('\n')
                    except:
                        continue
        if (len(ca_fails) > 0):
            csv_res_caerror.write("===============" + str(file_name) + "================")
            csv_res_caerror.write('\n')
            for tup in ca_fails:
                for  line in tup:
                    try:
                        csv_res_caerror.write(str(line))
                        csv_res_caerror.write('\n')
                    except:
                        continue
        if (len(deploy_fails) > 0):
            csv_res_deploymenterror.write("===============" + str(file_name) + "================")
            csv_res_deploymenterror.write('\n')
            for tup in deploy_fails:
                for  line in tup:
                    try:
                        csv_res_deploymenterror.write(str(line))
                        csv_res_deploymenterror.write('\n')
                    except:
                        continue
        if (len(travis_errors) > 0):
            csv_res_traviserror.write("===============" + str(file_name) + "================")
            csv_res_traviserror.write('\n')
            for tup in travis_errors:
                for line in tup:
                    try:
                        csv_res_traviserror.write(str(line))
                        csv_res_traviserror.write('\n')
                    except:
                        continue
    end_time_all = time.perf_counter()
    print(f"Execution Time : {end_time_all - start_time_all:0.6f}")


