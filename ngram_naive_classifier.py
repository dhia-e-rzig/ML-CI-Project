from pprint import pprint

import pandas as pd
import yaml
from nltk.util import ngrams
import nltk
import re
from Yaml_Utils import find_langs


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

df_bigrams=pd.read_csv('CSV Inputs/ngrams/bigrams.csv')


def transform_to_set_of_ngrams(list, n):
    result_set=set()
    for el in list:
        new_grams=extract_ngrams(el,n)
        result_set.update(new_grams)
    return result_set


bigrams_build_set=transform_to_set_of_ngrams(df_bigrams.loc[df_bigrams['Type'] == 'Build', '2-gram'].to_list(),2)
bigrams_test_set=transform_to_set_of_ngrams(df_bigrams.loc[df_bigrams['Type'] == 'Test', '2-gram'].to_list(),2)
bigrams_deploy_set=transform_to_set_of_ngrams(df_bigrams.loc[df_bigrams['Type'] == 'Deploy', '2-gram'].to_list(),2)
bigrams_ca_set=transform_to_set_of_ngrams(df_bigrams.loc[df_bigrams['Type'] == 'CodeAnalysis', '2-gram'].to_list(),2)



df_trigrams=pd.read_csv('CSV Inputs/ngrams/trigrams.csv')
trigrams_build_set=transform_to_set_of_ngrams(df_trigrams.loc[df_trigrams['Type'] == 'Build', '3-gram'].to_list(),3)
trigrams_test_set=transform_to_set_of_ngrams(df_trigrams.loc[df_trigrams['Type'] == 'Test', '3-gram'].to_list(),3)
trigrams_deploy_set=transform_to_set_of_ngrams(df_trigrams.loc[df_trigrams['Type'] == 'Deploy', '3-gram'].to_list(),3)
trigrams_ca_set=transform_to_set_of_ngrams(df_trigrams.loc[df_trigrams['Type'] == 'CodeAnalysis', '3-gram'].to_list(),3)


def analyze_file_using_ngrams(repo,filepath,n,output_df):
    if(n == 2):
       build_grams=bigrams_build_set
       test_grams=bigrams_test_set
       deploy_grams=bigrams_deploy_set
       ca_grams=bigrams_ca_set
    elif (n == 3):
        build_grams = trigrams_build_set
        test_grams = trigrams_test_set
        deploy_grams = trigrams_deploy_set
        ca_grams = trigrams_ca_set
    else:
        raise Exception("only 2 and 3 grams are currently supported")
    build_bool= False
    test_bool= False
    deploy_bool= False
    ca_bool= False
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
                        #filters that generaigy URLs and filepaths
                        line_list = ['URL' if re.findall(r'(http[s]?:\/\/)?([^\/\s]+\/)(.*)', x) else  x for x in line_list]
                        line_list = list(map(replace_with_generic_path,line_list))
                        line_list = ['FILE_PATH_TXT' if x.lower().endswith('.txt') else  x for x in line_list]
                        line_list = ['FILE_PATH_SH' if x.lower().endswith('.sh') else  x for x in line_list]
                        line_list = ['FILE_PATH_PY' if x.lower().endswith('.py') else  x for x in line_list]
                        line=' '.join(line_list)
                        exclude = {" , ", ", ", " ,", " .", " .", " . ", ":", ";", " ;", "; ", "=", "[", ']',
                                   "- ", " - ", "`", "'", "\"", "$", "&", "!", "--", '(', ')', '{', '}','<','>','|','@'
                                   ,"#","%"}
                        for ch in exclude:
                            line = line.replace(ch, ' ')
                        ngrams_temp=extract_ngrams(line,n)
                        ngrams_set.update(ngrams_temp)
                    if(len(ngrams_set.intersection(build_grams)) != 0):
                        build_bool=True
                        # print(ngrams_set.intersection(build_grams))
                    if (len(ngrams_set.intersection(test_grams)) != 0):
                        test_bool=True
                        # print(ngrams_set.intersection(test_grams))
                    if (len(ngrams_set.intersection(deploy_grams)) != 0):
                        deploy_bool=True
                        # print(ngrams_set.intersection(deploy_grams))
                    if (len(ngrams_set.intersection(ca_grams)) != 0):
                        ca_bool=True
                        # print(ngrams_set.intersection(ca_grams))
            except yaml.YAMLError as exc:
                print(exc)
    except Exception as e:
        if type(e) == FileNotFoundError:
            print('FileNotFound')
        else:
            print(str(e))
    output_df.loc[len(output_df.index)] = [ repo,filepath,build_bool, test_bool,deploy_bool,ca_bool]
    # return output_df


df_res = pd.DataFrame(columns=['Repository','FilePath', 'Build', 'Test','Deploy','CodeAnalysis'])

df_files=pd.read_csv('CSV Inputs/Travis_paths.csv',sep=';')
df_files.apply(lambda row: analyze_file_using_ngrams(row['RepoName'],row['TravisFullPath'],2,df_res),axis=1)

df_res.to_csv('tmp.csv',index=False)
