import csv
import json
import re
import nltk
from nltk.collocations import BigramCollocationFinder, BigramAssocMeasures
from nltk.util import ngrams
import pandas as pd
from pprint import pprint
import yaml
from nltk.tokenize import punkt
import string
from Yaml_Utils import find_langs
import math
import nltk
from collections import defaultdict

def extract_travis_files_paths():
    df_applied_projs=pd.read_csv('CSV Inputs/Projects_sets/applied_fs_and_api2.csv')
    applied_list=df_applied_projs['ProjectName'].to_list()
    df_tool_projs=pd.read_csv('CSV Inputs/Projects_sets/tool_fs_and_api2.csv')
    tool_list = df_tool_projs['ProjectName'].to_list()
    all_projs=applied_list+tool_list
    old_file_path = ''
    output= open('CSV Outputs/Travis_paths.csv', 'w+', encoding="utf8")
    output.write('RepoName;TravisFullPath;TravisFileGitURL')
    output.write('\n')
    df = pd.read_csv('./CSV Inputs/travis_commit-history-05-11-21-11-29-19-applied.csv', sep=";")
    df2 = pd.read_csv('./CSV Inputs/travis_commit-history-05-11-21-14-52-02-tool.csv', sep=";")
    df_l=[df,df2]
    previous_s=''
    for df in df_l:
        for row in df.itertuples():
            filepath = str(row[3])
            if 'deleted' in str(filepath).lower():
                continue
            if filepath == old_file_path:
                continue
            try:
                count_of_path= str(row[2]).count('\\') # testing relative path to see if travis file is at the root of the repo ( max under one subfolder is accepted)
                if count_of_path > 1:
                    continue
                if row[1] not in all_projs:
                    continue
                with open(filepath, 'r', encoding="utf8") as stream:
                    s_temp=stream.readline()
                s=str(row[1])+';'+str(row[3])+';'+str(row[4])
                if(previous_s == s):
                    continue
                else:
                    output.write(s)
                    output.write('\n')
                    previous_s = s
            except Exception as e:
                if type(e) == FileNotFoundError:
                    continue
                else:
                    print(str(e))



def extract_ngrams(data, num):
    n_grams = ngrams(nltk.word_tokenize(data), num)
    return [ ' '.join(grams) for grams in n_grams]


def replace_with_generic_path(x):
    string_return = x
    if re.findall(r'^\/$|(^(?=\/)|^.|^\.\.|.+)(\/(?=[^/\0])[^/\0]+)+\/?$', x):
        string_return = 'PATH'
        ext_beg=x.rfind('.')
        if ext_beg !=-1:
            ext=x[ext_beg+1:]
            if len(ext)<6:
                string_return+='_'+str(ext).upper()
    return string_return

def generate_ngrams(n):
    all_tokens_dict=dict()
    total_number_of_files=0
    df = pd.read_csv('./CSV Inputs/Travis_paths.csv',sep=";")
    old_file_path=''
    for row in df.itertuples():
        filepath=str(row[2])
        if 'deleted' in str(filepath).lower():
            continue
        if filepath == old_file_path:
            continue
        try:
            with open(filepath, 'r', encoding="utf8") as stream:
                try:
                    dicta= yaml.safe_load(stream)
                    langs=find_langs(dicta)
                    if ('Python' in langs) or ('python' in langs):
                        stream.seek(0)
                        lines = stream.readlines()
                        ngrams_set=set()
                        print(filepath)
                        for line in lines:
                            line=line.strip()
                            if line.startswith('#'):
                                continue
                            end_loc=line.find(' #')
                            if end_loc != -1:
                                line=line[:end_loc-1]
                            line = line.lower()
                            line=line.strip()
                            line_list=line.split(' ')
                            #filter that replaces paths with generic FILE_PATH

                            line_list = ['URL' if re.findall(r'(http[s]?:\/\/)?([^\/\s]+\/)(.*)', x) else  x for x in line_list]
                            line_list = list(map(replace_with_generic_path,line_list))
                            line_list = ['FILE_PATH_TXT' if x.lower().endswith('.txt') else  x for x in line_list]
                            line_list = ['FILE_PATH_SH' if x.lower().endswith('.sh') else  x for x in line_list]
                            line_list = ['FILE_PATH_PY' if x.lower().endswith('.py') else  x for x in line_list]
                            # add filter for numbers

                                # filter(lambda word: "URL" if re.findall(r'(http[s]?:\/\/)?([^\/\s]+\/)(.*)',
                                #                                         word) else word,
                                #        line_list))
                            # line_list = list(
                            #     filter(lambda word: "FILE_PATH" if re.findall(r'^\/$|(^(?=\/)|^\.|^\.\.)(\/(?=[^/\0])[^/\0]+)*\/?$',
                            #                                                   word) else word,
                            #            line_list))
                            # line_list = list(
                            #     filter(lambda word: "FILE_PATH" if word.lower().endswith('.txt')  else word,
                            #            line_list))
                            # line_list = list(
                            #     filter(lambda word: "FILE_PATH" if word.lower().endswith('.sh') else word,
                            #            line_list))
                            line=' '.join(line_list)
                            exclude = {" , ", ", ", " ,", " .", " .", " . ", ":", ";", " ;", "; ", "=", "[", ']',
                                       "- ", " - ", "`", "'", "\"", "$", "&", "!", "--", '(', ')', '{', '}','<','>','|','@'
                                       ,"#","%"}
                            for ch in exclude:
                                line = line.replace(ch, ' ')
                            ngrams_temp=extract_ngrams(line,n)
                            ngrams_set.update(ngrams_temp)
                        for elem in ngrams_set:
                            if elem in all_tokens_dict.keys():
                                all_tokens_dict[elem]+=1
                            else:
                                all_tokens_dict[elem]=1
                        ngrams_set.clear()
                        total_number_of_files+=1
                        print(total_number_of_files)
                except yaml.YAMLError as exc:
                    continue
        except Exception as e:
            if type(e) == FileNotFoundError:
                continue
            else:
                print(str(e))

    for key,value in all_tokens_dict.items():
        all_tokens_dict[key]=value/total_number_of_files
    labels = [str(n)+'-gram', 'Frequency']
    with open('CSV Outputs/Python_'+str(n)+'gram_with_freq_v2.csv', 'w+',newline='',encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(labels)
        for k, v in all_tokens_dict.items():
            writer.writerow([k, v])


generate_ngrams(2)
generate_ngrams(3)
