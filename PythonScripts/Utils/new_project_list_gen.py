import pandas as pd

# list_of_projects_df_rq2=pd.read_csv('../CSV Inputs/ListOfProjects-RQ2.csv')


# list_of_projects_df_rq3_4=pd.read_csv('../CSV Inputs/ListOfProjects-RQ3-RQ4.csv')


# ci_adoption_df_1=pd.read_csv('../CSV Input - New/CI Adoption - part 1.csv')
# ci_adoption_df_2=pd.read_csv('../CSV Input - New/CI Adoption - part 2.csv')


api2_travis=pd.read_csv('../CSV Input - New/all_travis_api_2.csv')

list_of_projects_tool=pd.read_csv('../CSV Inputs/Tool-classification.csv')
list_of_projects_applied=pd.read_csv('../CSV Inputs/Applied-classification.csv')

out_applied=open('../CSV Output - New/Travis_api2_Applied.csv','w+',encoding='utf-8')
# out_applied.write('projectName,AppVeyor,Azure,BuildBot,CircleCI,CloudBuild,CodeBuild,GitLab,Jenkins,Travis,VSTSCI,GithubA,CI?\n')

out_tool=open('../CSV Output - New/Travis_api2_Tool.csv','w+',encoding='utf-8')
# out_tool.write('projectName,AppVeyor,Azure,BuildBot,CircleCI,CloudBuild,CodeBuild,GitLab,Jenkins,Travis,VSTSCI,GithubA,CI?\n')

applied_found=[]
tool_found=[]
applied_projects = list_of_projects_applied['ProjectName'].tolist()
tool_projects = list_of_projects_tool['ProjectName'].tolist()
for tuples in api2_travis.itertuples():
    project_name=tuples[1]
    # print(project_name)
    # tuples_str=[str(x) for x in tuples[2:]]
    # string_out=",".join(tuples_str)
    if project_name in applied_projects:
        projectType='Applied'
        out_applied.write(project_name+'\n')
        # out_applied.flush()
        # applied_found.append(project_name)
    elif project_name in tool_projects:
        projectType='Tool'
        out_tool.write(project_name + '\n')
        # out_tool.flush()
        # tool_found.append(project_name)
    else:
        continue
        # RepoName, RepoType, GitHubURL
exit()

for tuples in ci_adoption_df_2.itertuples():
    project_name=tuples[1]
    # print(project_name)
    tuples_str = [str(x) for x in tuples[2:]]
    string_out = ",".join(tuples_str)
    if project_name in applied_projects:
        projectType='Applied'
    elif project_name in tool_projects:
        projectType='Tool'
    else:
        continue
        # RepoName, RepoType, GitHubURL
    if project_name in applied_projects:
        projectType = 'Applied'
        # out_applied.write(project_name + ',' + string_out + '\n')
        # out_applied.flush()
        applied_found.append(project_name)
    elif project_name in tool_projects:
        projectType = 'Tool'
        # out_tool.write(project_name + ',' + string_out + '\n')
        # out_tool.flush()
        tool_found.append(project_name)
    else:
        continue

notIn_origin_applied=[ x for x in applied_projects if x not in applied_found]
print(notIn_origin_applied)
notIn_origin_tool=[ x for x in tool_projects if x not in tool_found]
print(notIn_origin_tool)
exit()
df_applied_final=pd.read_csv('../CSV Input - New/final_output-10-13-21-10-47-16-applied.csv')
df_additional_applied=df_applied_final[df_applied_final['ProjectName'].isin(notIn_origin_applied)]
for tuples in df_additional_applied.itertuples():
    project_name=tuples[1]
    tuples_str=[str(x) for x in tuples[45:55]]
    string_out=",".join(tuples_str)
    string_out=string_out+','+str(tuples[-1])
    if 'true' in string_out.lower():
        bool_out='True'
    else:
        bool_out='False'
    out_applied.write(project_name+','+string_out+','+bool_out+'\n')
    # out_applied.write(project_name+','+string_out)


df_tool_final=pd.read_csv('../CSV Input - New/final_output-10-13-21-10-47-16-tool.csv')
df_additional_tool=df_tool_final[df_tool_final['ProjectName'].isin(notIn_origin_tool)]

for tuples in df_additional_tool.itertuples():
    project_name=tuples[1]
    tuples_str=[str(x) for x in tuples[45:55]]
    string_out=",".join(tuples_str)
    string_out=string_out+','+str(tuples[-1])
    if 'true' in string_out.lower():
        bool_out='True'
    else:
        bool_out='False'
    out_tool.write(project_name+','+string_out+','+bool_out+'\n')

#
# out_rq3=open('RQ3-RQ4-new-projects.csv','w+',encoding='utf-8')
# out_rq3.write('RepoName,RepoType,GitHubURL\n')
# for index,row in list_of_projects_df_rq3_4.iterrows():
#     applied_projects=list_of_projects_applied['ProjectName'].tolist()
#     tool_projects=list_of_projects_tool['ProjectName'].tolist()
#     project_name=row['RepoName']
#     print(project_name)
#     git_url=row['GitHubURL']
#     if project_name in applied_projects:
#         projectType='Applied'
#     elif project_name in tool_projects:
#         projectType='Tool'
#     else:
#         continue
#         # RepoName, RepoType, GitHubURL
#     out_rq3.write(project_name+','+projectType+','+git_url+'\n')
