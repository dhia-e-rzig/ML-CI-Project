import csv

import pandas

from PythonScripts.Utils import Github_Utils as GHUtils
from github import Github
from pprint  import pprint

from PythonScripts.Utils.Yaml_Utils import find_langs

gh= Github(GHUtils.get_github_token())
import datetime
import pandas as pd
import yaml
from collections import Counter

listOfTypes=["applied","tool",'nonml']
i = 2

# already_confirmed_df=pd.read_csv('..\\..\\CSV Inputs\\python_projects_with_travis_info.csv')
# list_already_confirmed_projects=already_confirmed_df['RepoName'].to_list()
# all_api2_df=pd.read_csv('..\\..\\CSV Outputs\\allprojects_travis_api_2_08_13_2021.csv')
# all_additional_api2_df=all_api2_df[~(all_api2_df['ProjectName'].isin(list_already_confirmed_projects))]
# print(len(all_api2_df))

projects_paths=['CSV Inputs/Projects_sets/applied_fs_and_api2.csv', 'CSV Inputs/Projects_sets/tool_fs_and_api2.csv']

commits_paths=['CSV Inputs/travis_commit-history-05-11-21-11-29-19-applied.csv', 'CSV Inputs/travis_commit-history-05-11-21-14-52-02-tool.csv']
travis_1ormore_build_paths=['CSV Inputs/applied_travis_api_2.csv','CSV Inputs/tool_travis_api_2.csv']

gh_langs_paths=['../../CSV Inputs/langs_gh_tool_08_24_2021.csv', '../../CSV Inputs/langs_gh_applied_08_24_2021.csv']
travis_langs_paths=['CSV Inputs/api2_and_fs_projects_stats/repos_langs_travis-05-28-21-17-35-57-applied.csv','CSV Inputs/api2_and_fs_projects_stats/repos_langs_travis-05-28-21-17-36-00-tool.csv']

# paths_repos=['D:/PhD Work/repos/applied','D:/PhD Work/repos/tool']


def get_langs_from_github():
    x = datetime.datetime.now()
    time = x.strftime("%x-%X").replace(":", "-").replace("/", "-")
    # type=listOfTypes[i]
    # path = projects_paths[i]
    output_file = open("non-ml_repos_langs-" + time  + ".csv", "w+", encoding="utf-8")
    output_file.write(
        "RepoName;RepoType;GitHubLanguages")
    output_file.write("\n")
    df_repos=pandas.read_csv('../../CSV Input - New/NonML-classification.csv')
    projects=df_repos['ProjectName'].tolist()
    for i in range(0,len(projects)):
        not_finished_because_of_rate_limit = True
        while (not_finished_because_of_rate_limit):
            try:
                print(projects[i])
                repo = gh.get_repo(projects[i])
                langs=repo.get_languages()
                sort_langauges = sorted(langs.items(), key=lambda x: x[1], reverse=True)
                langs=[]

                k=0
                for t in sort_langauges:
                    if (k >= 3):
                        break
                    if(t[0] == 'HTML') or (t[0] == 'CSS') or (t[0] == 'TeX'):
                        continue
                    langs.append(t[0])
                    k += 1

                langs_str = ",".join(langs)
                not_finished_because_of_rate_limit = False
                # if 'python' not in langs_str.lower():
                #     continue
                output_file.write(
                    projects[i]+';'+"NonML"+";"+langs_str)
                output_file.write("\n")
            except Exception as e:
                if GHUtils.is_over_core_rate(gh) or "API rate limit exceeded" in str(e):
                    GHUtils.sleep_until_core_rate_reset(gh)
                    i=i-1
                else:
                    print('Unknown exception: ' + str(e))
                    not_finished_because_of_rate_limit = False

def get_langs_travis(i):
    df_project=pandas.read_csv(projects_paths[i])
    projects_list=df_project['ProjectName'].to_list()
    x = datetime.datetime.now()
    time = x.strftime("%x-%X").replace(":", "-").replace("/", "-")
    type = listOfTypes[i]
    path = commits_paths[i]
    output_file = open("CSV Outputs/repos_langs_travis-" + time + "-" + type + ".csv", "w+", encoding="utf-8")
    output_file.write(
        "RepoName;TravisLanguages")
    output_file.write("\n")
    df_commits = pd.read_csv(path,sep=";")
    old_file_path=""
    old_project_name=list(df_commits.head(1).iterrows())[0][1][0]
    langs_t=set()
    langs_proj=set()
    for row in df_commits.itertuples():
        file_path=row[3]
        project_name=row[1]
        if project_name not in projects_list:
            continue
        # print(file_path)
        # print(project_name)
        if file_path == old_file_path:
            continue
        old_file_path = file_path
        if 'deleted' in file_path.lower():
            continue
        try:
            with open(file_path, 'rb') as stream:
                yml = yaml.safe_load(stream)
                langs_t= find_langs(yml)
        except Exception as e:
            if isinstance(e,yaml.YAMLError):
                continue
            if "No such file or directory" in str(e):
                continue
            else:
                print(str(e))
                print(project_name)
                exit()
        if project_name != old_project_name:
            if (len(langs_proj) == 0):
                langs_s = "None"
            else:
                langs_s = ','.join(langs_proj)
            output_file.write(old_project_name + ";" + langs_s)
            output_file.write("\n")
            langs_proj.clear()
        langs_proj.update(langs_t)
        old_project_name=project_name

    if (len(langs_proj) == 0):
        langs_s = "None"
    else:
        langs_s = ','.join(langs_proj)
    last_project_name = list(df_commits.tail(1).iterrows())[0][1][0]
    output_file.write(last_project_name + ";" + langs_s)
    output_file.write("\n")

def lower(ele):
    return str(ele).lower()

def unify_cpp_notation(ele):
    if ele == 'cpp':
        return 'c++'
    else:
        return ele

def clean_values(ele):
    return str(ele).strip().replace("'","").replace('"','')


def get_contradiction(i):
    gh_path=gh_langs_paths[i]
    travis_path=travis_langs_paths[i]
    x = datetime.datetime.now()
    time = x.strftime("%x-%X").replace(":", "-").replace("/", "-")
    type = listOfTypes[i]
    gh_df=pd.read_csv(gh_path,sep=";")
    travis_df=pd.read_csv(travis_path,sep=";")
    output_file = open("CSV Outputs/repos_langs_diff-" + time + "-" + type + ".csv", "w+", encoding="utf-8")
    output_file.write(
        "RepoName;TravisAndGHMatch;Intersection;TravisOnly;GithubOnly")
    output_file.write("\n")
    for row in travis_df.itertuples():
        repo_name=row[1]
        langs_s=row[2]
        if "," in langs_s:
            langs_list=langs_s.split(',')
        else:
            langs_list=langs_s
        if isinstance(langs_list,list) :
            langs_list= list(map(lower, langs_list))
            langs_list= list(map(unify_cpp_notation, langs_list))
            langs_list= list(map(clean_values, langs_list))
            langs_set = set(langs_list)
        else:
            langs_set=set()
            langs_set.add(clean_values(unify_cpp_notation(langs_list)))
        repo_row=gh_df.loc[gh_df['RepoName'] == repo_name].head(1)
        try:
            gh_langs=str(repo_row['GitHubLanguages'].to_list()).replace('[','').replace(']','').split(',')
            lower_list = list(map(lower, gh_langs))
            lower_list = list(map(clean_values, lower_list))
            gh_langs_set=set(lower_list)
            # print(langs_set)
            # print(gh_langs_set)
            intersection=langs_set.intersection(gh_langs_set)
            intersection_s=",".join(intersection)
            travisonly=langs_set.difference(gh_langs_set)
            travisonly_s = ",".join(travisonly)
            githubonly=gh_langs_set.difference(langs_set)
            githubonly_s = ",".join(githubonly)
            if len(intersection) > 0:
                # output_file.write("RepoName;TravisAndGHMatch;Intersection;TravisOnly;GithunOnly")
                output_file.write(repo_name+';True'+';'+intersection_s+';'+travisonly_s+';'+githubonly_s)
                output_file.write("\n")
            else:
                if('node_js' in travisonly_s and 'javascript' in githubonly_s) or ('node_js' in travisonly_s and 'typescript' in githubonly_s) or ('csharp' in travisonly_s and 'c#' in githubonly_s) or ('csharp' in travisonly_s and 'f#' in githubonly_s) or ('bash' in travisonly_s and 'shell' in githubonly_s) :
                    output_file.write(repo_name + ';True' + ';' + intersection_s + ';' + travisonly_s + ';' + githubonly_s)
                else:
                    output_file.write(
                        repo_name + ';False' + ';' + intersection_s + ';' + travisonly_s + ';' + githubonly_s)
                output_file.write("\n")
        except Exception as e:
            print(e)
            output_file.write(repo_name + ';NotInGithub' + ';' + ';' + ';' )
            output_file.write("\n")


def get_frequency_of_langs():
    all_langs_list_tool=[]
    gh_langs_df_applied = pd.read_csv( '../../CSV Archives/Ci Adoption folder/non-ml_repos_langs-03-16-22-09-25-00.csv',sep=';')
    for row in gh_langs_df_applied.itertuples():
        if isinstance(row[3], str):
            gh_langs = row[3].split(',')
            temp_l = list(map(clean_values, gh_langs))
            if ('HTML' in temp_l[0]):
                temp_l.pop(0)
            if (len(temp_l) > 0 and 'CSS' in temp_l[0]):
                temp_l.pop(0)
            if (len(temp_l) > 0 and 'TeX' in temp_l[0]):
                temp_l.pop(0)
            if (len(temp_l) > 0):
                all_langs_list_tool.append(temp_l[0])
    al = Counter(all_langs_list_tool).most_common()
    with open('../../CSV Output - New/PrimaryLanguageCount-nonML_new.csv', 'w', newline='') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(['Language', 'Frequency'])
        for row in al:
            csv_out.writerow(row)

def get_langs_not_on_gh(i):
    gh_path=gh_langs_paths[i]
    travis_path=projects_paths[i]
    gh_df=pd.read_csv(gh_path,sep=";")
    travis_df=pd.read_csv(travis_path)
    gh_projects=gh_df['RepoName']
    travis_projects=travis_df['ProjectName']
    gh_projects=[str(item).replace("'",'') for item in gh_projects]
    not_gh = [item for item in travis_projects if item not in gh_projects]
    pprint(not_gh)

# get_langs_gh(0)
# get_langs_travis(0)
# get_langs_gh(1)
# get_langs_travis(1)
#
# get_contradiction(0)
# get_contradiction(1)
# get_frequency_of_langs()

# get_langs_not_on_gh(0)
# get_langs_travis(0)

# get_langs_gh()

# get_frequency_of_langs()

def filter_langs():
    df_1=pd.read_csv('../../CSV Inputs/api2_and_fs_projects_stats/repos_additional_langs_github-08-13-21-14-01-26.csv',sep=';')
    df_2=pd.read_csv('../../CSV Inputs/api2_and_fs_projects_stats/repos_langs_github-05-27-21-14-38-27-tool.csv',sep=';')
    df_3=pd.read_csv('../../CSV Inputs/api2_and_fs_projects_stats/repos_langs_github-05-27-21-14-35-24-applied.csv',sep=';')
    Langs_Travis_tool_API2=open('../../CSV Inputs/langs_gh_tool_08_24_2021.csv','w+',encoding='utf-8')
    Langs_Travis_applied_API2=open('../../CSV Inputs/langs_gh_applied_08_24_2021.csv','w+',encoding='utf-8')
    Langs_Travis_tool_API2.write('RepoName;GitHubLanguages\n')
    Langs_Travis_applied_API2.write('RepoName;GitHubLanguages\n')
    # projects_to_keep=all_api2_df['ProjectName'].tolist()
    projects_to_keep=pd.read_csv('../../CSV Input - New/RQ1_Applied_New.csv')['ProjectName'].tolist()+pd.read_csv('../../CSV Input - New/RQ1_Tool_New.csv')['ProjectName'].tolist()
    df_1.fillna('0',inplace=True)
    df_2.fillna('0',inplace=True)
    df_3.fillna('0',inplace=True)
    repos_found=[]
    for  index,row in df_1.iterrows():
        print(row['RepoName'])
        print(row['GitHubLanguages'])
        if row['RepoName'] in projects_to_keep:
            if row['RepoName'] not in repos_found:
                repos_found.append(row['RepoName'])
            else:
                continue
            if row['RepoType'] == 'Tool':
                Langs_Travis_tool_API2.write(str(row['RepoName'])+';'+str(row['GitHubLanguages'])+'\n')
            else:
                Langs_Travis_applied_API2.write(str(row['RepoName']) + ';' + str(row['GitHubLanguages'])+'\n')

    for index,row in df_2.iterrows():
        if row['RepoName'] in projects_to_keep:
            if row['RepoName'] not in repos_found:
                repos_found.append(row['RepoName'])
            else:
                continue
            Langs_Travis_tool_API2.write(str(row['RepoName']) + ';' + str(row['GitHubLanguages'])+'\n')

    for index, row in df_3.iterrows():
        if row['RepoName'] in projects_to_keep:
            if row['RepoName'] not in repos_found:
                repos_found.append(row['RepoName'])
            else:
                continue
            Langs_Travis_applied_API2.write(str(row['RepoName']) + ';' + str(row['GitHubLanguages'])+'\n')

get_langs_from_github()
