import string

import pandas as pd
import yaml
from nltk.util import ngrams
import nltk
import re
from PythonScripts.Utils.Yaml_Utils import find_langs
from shutil import copyfile

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

df_bigrams=pd.read_csv('../../CSV Inputs/ngrams/bigrams.csv')
df_unigrams=pd.read_csv('CSV Inputs/ngrams/unigrams_Travis.csv')


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


unigram_build_set=set(df_unigrams.loc[df_unigrams['Type'] == 'Build', '1-gram'].to_list())
unigram_test_set=set(df_unigrams.loc[df_unigrams['Type'] == 'Test', '1-gram'].to_list())
unigram_deploy_set=set(df_unigrams.loc[df_unigrams['Type'] == 'Deploy', '1-gram'].to_list())
unigram_ca_set=set(df_unigrams.loc[df_unigrams['Type'] == 'CodeAnalysis', '1-gram'].to_list())

df_trigrams=pd.read_csv('../../CSV Inputs/ngrams/trigrams.csv')
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


def analyze_file_using_allgrams(repo, filepath, output_df):
    build_trigrams = trigrams_build_set
    test_trigrams = trigrams_test_set
    deploy_trigrams = trigrams_deploy_set
    ca_trigrams = trigrams_ca_set

    build_bigrams = bigrams_build_set
    test_bigrams = bigrams_test_set
    deploy_bigrams = bigrams_deploy_set
    ca_bigrams = bigrams_ca_set

    build_unigrams = unigram_build_set
    test_unigrams = unigram_test_set
    deploy_unigrams = unigram_deploy_set
    ca_unigrams = unigram_ca_set

    build_bool = False
    test_bool = False
    deploy_bool = False
    ca_bool = False
    try:
        with open(filepath, 'r', encoding="utf8") as stream:
            try:
                dicta = yaml.safe_load(stream)
                langs = find_langs(dicta)
                if ('Python' in langs) or ('python' in langs):
                    stream.seek(0)
                    lines = stream.readlines()
                    trigrams_set = set()
                    bigrams_set = set()
                    unigrams_set = set()
                    print(filepath)
                    for line in lines:
                        line = line.strip()
                        if line.startswith('#'):
                            continue
                        end_loc = line.find(' #')
                        if end_loc != -1:
                            line = line[:end_loc - 1]
                        line = line.lower()
                        line = line.strip()
                        line_list = line.split(' ')
                        # filters that generaigy URLs and filepaths
                        line_list = ['URL' if re.findall(r'(http[s]?:\/\/)?([^\/\s]+\/)(.*)', x) else x for x in
                                     line_list]
                        line_list = list(map(replace_with_generic_path, line_list))
                        line_list = ['FILE_PATH_TXT' if x.lower().endswith('.txt') else x for x in line_list]
                        line_list = ['FILE_PATH_SH' if x.lower().endswith('.sh') else x for x in line_list]
                        line_list = ['FILE_PATH_PY' if x.lower().endswith('.py') else x for x in line_list]
                        line = ' '.join(line_list)
                        exclude = {" , ", ", ", " ,", " .", " .", " . ", ":", ";", " ;", "; ", "=", "[", ']',
                                   "- ", " - ", "`", "'", "\"", "$", "&", "!", "--", '(', ')', '{', '}', '<', '>', '|',
                                   '@'
                            , "#", "%"}
                        for ch in exclude:
                            line = line.replace(ch, ' ')
                        ngrams_temp = extract_ngrams(line, 3)
                        trigrams_set.update(ngrams_temp)
                        ngrams_temp = extract_ngrams(line, 2)
                        bigrams_set.update(ngrams_temp)
                        ngrams_temp = extract_ngrams(line, 1)
                        unigrams_set.update(ngrams_temp)
                    # ngrams_diff_1 = set()
                    if (len(trigrams_set.intersection(build_trigrams)) != 0):
                        build_bool = True
                        # ngrams_diff_1.update(trigrams_set.difference(build_trigrams))
                    if (len(trigrams_set.intersection(test_trigrams)) != 0):
                        test_bool = True
                        # ngrams_diff_1.update(trigrams_set.difference(test_trigrams))
                    if (len(trigrams_set.intersection(deploy_trigrams)) != 0):
                        deploy_bool = True
                        # ngrams_diff_1.update(trigrams_set.difference(deploy_trigrams))
                    if (len(trigrams_set.intersection(ca_trigrams)) != 0):
                        ca_bool = True
                        # ngrams_diff_1.update(trigrams_set.difference(ca_trigrams))

                    # remaining_bigrams = transform_to_set_of_ngrams(list(ngrams_diff_1),2)

                    # ngrams_diff_2=set()
                    if (len(bigrams_set.intersection(build_bigrams)) != 0):
                        build_bool = True
                        # ngrams_diff_2.update(trigrams_set.difference(build_bigrams))
                    if (len(bigrams_set.intersection(test_bigrams)) != 0):
                        test_bool = True
                        # ngrams_diff_2.update(trigrams_set.difference(test_bigrams))
                    if (len(bigrams_set.intersection(deploy_bigrams)) != 0):
                        deploy_bool = True
                        # ngrams_diff_2.update(trigrams_set.difference(deploy_bigrams))
                    if (len(bigrams_set.intersection(ca_bigrams)) != 0):
                        ca_bool = True
                        # ngrams_diff_2.update(trigrams_set.difference(ca_bigrams))

                    if (len(unigrams_set.intersection(build_unigrams)) != 0):
                        build_bool = True

                    if (len(unigrams_set.intersection(test_bigrams)) != 0):
                        test_bool = True

                    if (len(unigrams_set.intersection(deploy_unigrams)) != 0):
                        deploy_bool = True

                    if (len(unigrams_set.intersection(ca_unigrams)) != 0):
                        ca_bool = True



            except yaml.YAMLError as exc:
                print(exc)
    except Exception as e:
        if type(e) == FileNotFoundError:
            print('FileNotFound')
        else:
            print(str(e))
    output_df.loc[len(output_df.index)] = [repo, filepath, build_bool, test_bool, deploy_bool, ca_bool]


def analyze_file_using_bigrams_and_unigrams(repo,filepath,output_df):
    build_bigrams=bigrams_build_set
    test_bigrams=bigrams_test_set
    deploy_bigrams=bigrams_deploy_set
    ca_bigrams=bigrams_ca_set

    build_unigrams=unigram_build_set
    test_unigrams=unigram_test_set
    deploy_unigrams=unigram_deploy_set
    ca_unigrams=unigram_ca_set

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
                    unigram_set=set()
                    print(filepath)
                    for line in lines:
                        line=line.strip()
                        if line.startswith('#'):
                            continue
                        end_loc=line.find(' #')
                        if end_loc != -1:
                            line=line[:end_loc-1]
                        line = line.lower()
                        unigram_temp = re.split("[" + string.punctuation + "]+", line)
                        unigram_temp2=set()
                        for el in unigram_temp:
                            for el1 in re.split('\s+',el):
                                unigram_temp2.add(el1)
                        unigram_set.update(unigram_temp2)
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
                        ngrams_temp=extract_ngrams(line,2)
                        ngrams_set.update(ngrams_temp)
                        unigram_temp=extract_ngrams(line,1)
                        unigram_set.update(unigram_temp)
                    # pprint(unigram_set)
                    # exit()
                    # ngrams_diff=set()
                    if(len(ngrams_set.intersection(build_bigrams)) != 0):
                        build_bool=True
                        # ngrams_diff.update(ngrams_set.difference(build_bigrams))
                    if (len(ngrams_set.intersection(test_bigrams)) != 0):
                        test_bool=True
                        # ngrams_diff.update(ngrams_set.difference(test_bigrams))
                    if (len(ngrams_set.intersection(deploy_bigrams)) != 0):
                        deploy_bool=True
                        # ngrams_diff.update(ngrams_set.difference(deploy_bigrams))
                    if (len(ngrams_set.intersection(ca_bigrams)) != 0):
                        ca_bool=True
                        # ngrams_diff.update(ngrams_set.difference(ca_bigrams))
                    # unigram_set_temp=set()
                    # for el in unigram_set:
                    # unigram_set.update(unigram_set_temp)
                    # pprint(unigram_set)
                    # exit()

                    if (len(unigram_set.intersection(build_unigrams)) != 0):
                        build_bool = True
                        # ngrams_diff.update(ngrams_set.difference(build_unigrams))
                    if (len(unigram_set.intersection(test_unigrams)) != 0):
                        test_bool = True
                        # ngrams_diff.update(ngrams_set.difference(test_unigrams))
                    if (len(unigram_set.intersection(deploy_unigrams)) != 0):
                        deploy_bool = True
                        # ngrams_diff.update(ngrams_set.difference(deploy_unigrams))
                    if (len(unigram_set.intersection(ca_unigrams)) != 0):
                        ca_bool = True
                        # ngrams_diff.update(ngrams_set.difference(ca_unigrams))
                        
                    
            except yaml.YAMLError as exc:
                print(exc)
    except Exception as e:
        if type(e) == FileNotFoundError:
            print('FileNotFound')
        else:
            print(str(e))
    output_df.loc[len(output_df.index)] = [ repo,filepath,build_bool, test_bool,deploy_bool,ca_bool]


def analyze_file_using_unigrams(repo, filepath, output_df):

    build_unigrams = unigram_build_set
    test_unigrams = unigram_test_set
    deploy_unigrams = unigram_deploy_set
    ca_unigrams = unigram_ca_set

    build_bool = False
    test_bool = False
    deploy_bool = False
    ca_bool = False
    try:
        with open(filepath, 'r', encoding="utf8") as stream:
            try:
                dicta = yaml.safe_load(stream)
                langs = find_langs(dicta)
                if ('Python' in langs) or ('python' in langs):
                    stream.seek(0)
                    lines = stream.readlines()
                    ngrams_set = set()
                    unigram_set = set()
                    print(filepath)
                    for line in lines:
                        line = line.strip()
                        if line.startswith('#'):
                            continue
                        end_loc = line.find(' #')
                        if end_loc != -1:
                            line = line[:end_loc - 1]
                        line = line.lower()
                        unigram_temp = re.split("[" + string.punctuation + "]+", line)
                        unigram_temp2 = set()
                        for el in unigram_temp:
                            for el1 in re.split('\s+', el):
                                unigram_temp2.add(el1)
                        unigram_set.update(unigram_temp2)

                        unigram_temp = extract_ngrams(line, 1)
                        unigram_set.update(unigram_temp)

                    if (len(unigram_set.intersection(build_unigrams)) != 0):
                        build_bool = True
                        # ngrams_diff.update(ngrams_set.difference(build_unigrams))
                    if (len(unigram_set.intersection(test_unigrams)) != 0):
                        test_bool = True
                        # ngrams_diff.update(ngrams_set.difference(test_unigrams))
                    if (len(unigram_set.intersection(deploy_unigrams)) != 0):
                        deploy_bool = True
                        # ngrams_diff.update(ngrams_set.difference(deploy_unigrams))
                    if (len(unigram_set.intersection(ca_unigrams)) != 0):
                        ca_bool = True
                        # ngrams_diff.update(ngrams_set.difference(ca_unigrams))
            except yaml.YAMLError as exc:
                print(exc)
    except Exception as e:
        if type(e) == FileNotFoundError:
            print('FileNotFound')
        else:
            print(str(e))
    output_df.loc[len(output_df.index)] = [repo, filepath, build_bool, test_bool, deploy_bool, ca_bool]


def copy_files_to_one_loc(repo,filepath):
    try:
        with open(filepath, 'r', encoding="utf8") as stream:
            try:
                print(filepath)
                dicta= yaml.safe_load(stream)
                langs=find_langs(dicta)
                if ('Python' in langs) or ('python' in langs):
                    copyfile(filepath,'D:\\travisPyFiles\\'+str(repo).replace('/','_')+'_'+str(filepath).split('/')[-1])

            except yaml.YAMLError as exc:
                print(exc)
    except Exception as e:
        if type(e) == FileNotFoundError:
            print(str(e))
        else:
            print(str(e))

applied_repos_df=pd.read_csv('../../CSV Inputs/Projects_sets/applied_fs_and_api2.csv')
tool_repos_df=pd.read_csv('../../CSV Inputs/Projects_sets/tool_travis_api_2.csv')



from PyTravisCI import defaults, TravisCI
travis_access_com = TravisCI(access_token="yY5Pnt7Mgec81-8mAWc2aQ", access_point=defaults.access_points.PRIVATE)
travis_access_org = TravisCI(access_token="bYlcgiscf4elZlPEn8zlaQ")

def list_csvs_with_types(repo,filepath,output_file):
    try:
        with open(filepath, 'r', encoding="utf8") as stream:
            try:
                print(filepath)
                dicta= yaml.safe_load(stream)
                langs=find_langs(dicta)
                if ('Python' in langs) or ('python' in langs):
                    github_url="https://github.com/"+repo+".git"
                    file_url="https://github.com/"+repo+"/blob/master/.travis.yml"
                    try:
                        travis_repo=travis_access_com.get_repository(repo)
                        travis_url="https://travis-ci.com/"+repo
                    except:
                        try:
                            travis_repo = travis_access_org.get_repository(repo)
                            travis_url = "https://travis-ci.org/" + repo
                        except:
                            travis_url="No Travis URL"
                    if repo in applied_repos_df['ProjectName'].tolist():
                        output_file.write(repo+',Applied,'+filepath+','+file_url+','+travis_url+','+github_url)
                        output_file.write('\n')
                    if repo in tool_repos_df['ProjectName'].tolist():
                        output_file.write(repo + ',Tool,' + filepath+','+file_url+','+travis_url+','+github_url)
                        output_file.write('\n')
            except yaml.YAMLError as exc:
                print(exc)
    except Exception as e:
        if type(e) == FileNotFoundError:
            print(str(e))
        else:
            print(str(e))



# df_res = pd.DataFrame(columns=['Repository','FilePath', 'Build', 'Test','Deploy','CodeAnalysis'])

output_file=open('../../CSV Inputs/python_projects_with_travis_info.csv', 'w')
output_file.write('RepoName,RepoType,TravisFilePath,Travis+FileURL,GithubFileURLl,TravisRepoURL,GithubRepoURL')
output_file.write('\n')

df_files=pd.read_csv('../../CSV Inputs/all_projects_travis_paths.csv', sep=';')
# df_files.apply(lambda row: analyze_file_using_unigrams(row['RepoName'],row['TravisFullPath'],df_res),axis=1)
df_files.apply(lambda row: list_csvs_with_types(row['RepoName'],row['TravisFullPath'],output_file),axis=1)

# df_res.to_csv('1pass_unigram_travis.csv',index=False)
