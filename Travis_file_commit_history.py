from pydriller import Repository, ModificationType,Git
import datetime
import pandas as pd
import os.path
from os import path
import re

listOfTypes=["applied","tool","no-ai-ml"]
i= 1
type_travis_ci_pths=["CSV Inputs/applied_travis_fs_or_api.csv",'CSV Inputs/tool_travis_fs_or_api.csv']

applied_repos_local=['D:/PhD Work/repos/applied','D:/PhD Work/repos/applied']
tool_repos_local=['D:/PhD Work/repos/tool','D:/PhD Work/repos/tool']
paths_repos=[applied_repos_local,tool_repos_local]


def generate_travis_yml_commit_history(i):
    x = datetime.datetime.now()
    time = x.strftime("%x-%X").replace(":", "-").replace("/", "-")
    type = listOfTypes[i]
    output_file = open("CSV Outputs/travis_commit-history-" + time + "-" + type + ".csv", "w+", encoding="utf-8")
    output_file.write("RepoName;TravisRelativePath;TravisFullPath;TravisFileGitURL;CommitHash;CommitTimeStamp;CommitMessage")
    output_file.write("\n")
    output_file2 = open("CSV Outputs/travis_commit-history-with_file-diffs-" + time + "-" + type + ".csv", "w+", encoding="utf-8")
    output_file2.write("RepoName;TravisFilePath;TravisFileGitURL;CommitHash;CommitTimeStamp;CommitMessage;FileDIFF")
    output_file2.write('\n')
    output_file3 = open("CSV Outputs/travis_repos_no_file_found_in_hist-" + time + "-" + type + ".csv", "w+",
                        encoding="utf-8")
    output_file3.write("RepoName;RepoPath")
    output_file3.write('\n')
    error_file = open("CSV Outputs/travis_commit-history-errors-" + time + "-" + type + ".csv", "w+", encoding="utf-8")
    error_file.write("RepoName;Exception")
    error_file.write("\n")

    travis_projects_file=pd.read_csv(type_travis_ci_pths[i])
    travis_projects=travis_projects_file['ProjectName']
    paths=paths_repos[i]
    i=0
    total = len(travis_projects)
    for project in travis_projects:
        i+=1
        if path.exists(paths[0]+'/'+project):
            project_path = paths[0]+'/'+project
        elif path.exists(paths[1]+'/'+ project):
            project_path = paths[1] +'/'+ project
        else:
            error_file.write(project+',project not found in either folder locally')
            error_file.write('\n')
            continue
        try:
            git_repo = Git(project_path)
            commits_ids=git_repo.get_commits_modified_file('.travis.yml')
            commits_ids_2=git_repo.get_commits_modified_file('**/.travis.yml')
            commit_ids_set=list(set(commits_ids+commits_ids_2))
            for commit_id in commit_ids_set:
                commit=git_repo.get_commit(commit_id)
                paths_and_diffs_list = list([(x.old_path,x.new_path,x.diff) for x in commit.modified_files if '.travis.yml' == x.filename.lower()])
                for temp_path_and_diff in paths_and_diffs_list:
                    old_path=temp_path_and_diff[0]
                    temp_path=temp_path_and_diff[1]
                    temp_diff=temp_path_and_diff[2]
                    if temp_path is None:
                        if old_path is None:
                            temp_path='Deleted'
                        else:
                            temp_path=old_path+' -Deleted'
                    sentence=commit.msg.replace(';', ',')
                    sentence = re.sub(r"\s+", " ", sentence, flags=re.UNICODE)
                    if temp_path == 'Deleted':
                        url='Deleted'
                    else:
                        branches=list(commit.branches)
                        url="https://github.com/"+project+'/blob/'+branches[0]+'/'+temp_path.replace('\\','/')
                    full_path=project_path+'/'+temp_path.replace('\\','/')
                    string_out=project+';'+temp_path+';'+full_path+';'+url+';'+commit.hash+';'+str(commit.committer_date)+';'+sentence
                    # print(string_out)
                    output_file.write(string_out)
                    output_file.write('\n')
                    if temp_diff is None:
                        temp_diff='Deleted'
                    temp_diff=temp_diff.replace(';',',')
                    temp_diff=re.sub(r"\s+", " ", temp_diff, flags=re.UNICODE)
                    string_out2=string_out+';'+temp_diff
                    output_file2.write(string_out2)
                    output_file2.write('\n')

            if(len(commit_ids_set) == 0):
                    output_file3.write(project+';'+project_path)
                    output_file3.write('\n')

            percentage = "{:.4f}".format((i/total)*100)
            print('project '+project+' nb '+str(i)+' out of '+str(total)+' has been processed '+percentage+'% complete')
        except Exception as e:
            error_file.write(project+';'+str(e))
            error_file.write('\n')

            print(project+';'+str(e))

generate_travis_yml_commit_history(1)