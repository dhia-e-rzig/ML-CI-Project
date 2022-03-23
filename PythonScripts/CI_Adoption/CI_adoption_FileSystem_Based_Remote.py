import re

from PythonScripts.Utils import Github_Utils as GHU
import pandas as pd
from github import Github
import wget
# df_applied=pd.read_csv('../../CSV Inputs/AppliedProjects_classification.csv')
df_tool=pd.read_csv('../../CSV Inputs/ToolProjects_classification.csv')
with open("..\\..\\CSV Inputs\\ConfigFiles_for_CI_tool_detection.xlsx","rb") as configFile:
    tools_and_files=pd.read_excel(configFile)

tools_and_files_tups=tools_and_files[tools_and_files['Category']=="Continuous Integration"] [['Tool','Files']].values.tolist()
g=Github(GHU.get_github_token())

def find_easeml_ci(projectName):
    easeML_found=False
    not_finished_because_of_rate_limit = True
    list_of_tools_found=[]
    while(not_finished_because_of_rate_limit):
        try:
            repo=g.get_repo(full_name_or_id=projectName)
            Contentfiles=repo.get_contents(path='.')
            travis_files=[f for f in Contentfiles if f.name.lower()=='.travis.yml']
            travis_file=travis_files[0]
            print('downloading travis')
            wget.download(travis_file.download_url,'temp_travis.yml')
            print('downloaded travis')
            pattern=r'^ML:'
            with open('temp_travis.yml', 'r') as file_obj:
                Lines = file_obj.readlines()
                for line in Lines:
                    if re.compile(pattern).search(line):
                        print('ease.ml found')
                        easeML_found=True
                        return easeML_found
            not_finished_because_of_rate_limit=False
        except Exception as e:
            if GHU.is_over_core_rate(g) or "API rate limit exceeded" in str(e):
                GHU.sleep_until_core_rate_reset(g)
                list_of_tools_found.clear()
            else:
                print('Unknown exception: ' + str(e))
                not_finished_because_of_rate_limit = False
    return easeML_found

def find_fs_ci_on_gh(projectName):
    not_finished_because_of_rate_limit = True
    list_of_tools_found=[]
    while(not_finished_because_of_rate_limit):
        try:
            repo=g.get_repo(full_name_or_id=projectName)
            Contentfiles=repo.get_contents(path='.')
            file_names=[f.name for f in Contentfiles]
            for tool,file in tools_and_files_tups:
                matching_files=[f for f in file_names if f == file  ]
                if len(matching_files) !=0:
                     list_of_tools_found.append(tool)
            not_finished_because_of_rate_limit=False
        except Exception as e:
            if GHU.is_over_core_rate(g) or "API rate limit exceeded" in str(e):
                GHU.sleep_until_core_rate_reset(g)
                list_of_tools_found.clear()
            else:
                print('Unknown exception: ' + str(e))
                not_finished_because_of_rate_limit = False
    return list_of_tools_found


f_out = open('CI_adoption_tool.csv','w+',encoding='utf-8')
f_out.write("projectName,AppVeyor,Azure,BuildBot,CircleCI,CloudBuild,CodeBuild,GitLab,Jenkins,Travis,VSTSCI,GithubA,easeML")
f_out.write('\n')

for index,row in df_tool.iterrows():
    projectName=row['ProjectName']
    tools_found=find_fs_ci_on_gh(projectName)
    print(projectName,tools_found)
    AppVeyor=False
    Azure=False
    BuildBot=False
    CircleCI=False
    CloudBuild=False
    CodeBuild=False
    GitLab=False
    Jenkins=False
    VSTSCI=False
    Travis=False
    GithubA=False
    easeML=False
    if 'AppVeyor' in tools_found:
        AppVeyor=True
    if 'Azure Pipeline' in tools_found:
        Azure=True
    if 'BuildBot' in tools_found:
        BuildBot=True
    if 'CircleCI' in tools_found:
        CircleCI=True
    if 'CloudBuild' in tools_found:
        CloudBuild=True
    if 'CodeBuild' in tools_found:
        CodeBuild=True
    if 'GitLab Ci' in tools_found:
        GitLab=True
    if 'Jenkins' in tools_found:
        Jenkins=True
    if 'Travis' in tools_found:
        Travis=True
        easeML=find_easeml_ci(projectName)
    if 'VSTSCI' in tools_found:
        VSTSCI=True
    if 'Github Actions' in tools_found:
        GithubA=True
    # print(projectName+','+str(AppVeyor)+','+str(Azure)+','+str(BuildBot)+','+str(CircleCI)+','+str(CloudBuild)+','+str(CodeBuild)+','+str(GitLab)+','+str(Jenkins)+','+str(Travis)+','+str(VSTSCI)+','+str(GithubA))
    f_out.write(projectName+','+str(AppVeyor)+','+str(Azure)+','+str(BuildBot)+','+str(CircleCI)+','+str(CloudBuild)+','+str(CodeBuild)+','+str(GitLab)+','+str(Jenkins)+','+str(Travis)+','+str(VSTSCI)+','+str(GithubA)+','+str(easeML))
    f_out.write('\n')
