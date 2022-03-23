import pandas as pd

new_project_df=pd.read_csv('../CSV Input - New/RQ3-RQ4-new.csv')
project_list=new_project_df['RepoName'].tolist()
project_list=[p.replace('/','_') for p in project_list]
project_types=new_project_df['RepoType'].tolist()
output_file_applied= open('../CSV Output - New/classification_testfail_only_ml_subtype_08_10_2021_first_subtype_v3_NEW.csv', 'w+')
output_file_applied.write("file_name;TestFail;BuildError;TestError;CodeAnalysisError;TravisError;DeploymentError;RepoType\n")
# output_file_tool= open('../CSV Output - New/Tool_transition_with_problem_NEW.csv', 'w+')
# output_file_tool.write("repoUrl,failCommit,passCommit,mainProblem,allProblems,problemBuildState,RepoType\n")
with open('../CSV Input - New/classification_testfail_only_ml_subtype_08_10_2021_first_subtype_v3.csv','r') as fileobj:
    while (True):
        line = fileobj.readline()
        if not line:
            break
        file_path=line.split(',')[0]
        # print(file_path)
        line=line.replace('\n','')
        if('\\') not in file_path:
            continue
        project_name=file_path.split('\\')[7]
        # project_name=project_name[:-4]
        if project_name in project_list:
            project_index=project_list.index(project_name)
            project_type=project_types[project_index]
            # if project_type == 'Applied':
            output_file_applied.write(line + ';' + project_type + '\n')
            # else:
            #     output_file_tool.write(line + ',' + project_type + '\n')
        else:
            continue

#
# with open('../CSV Input - New/Tool_transition_with_problem.csv','r') as fileobj:
#     while (True):
#         line = fileobj.readline()
#         if not line:
#             break
#         file_path = line.split(',')[0]
#         # print(file_path)
#         line = line.replace('\n', '')
#         if ('/') not in file_path:
#             continue
#         project_name = file_path.split('/')[3] + '/' + file_path.split('/')[4]
#         project_name = project_name[:-4]
#         if project_name in project_list:
#             project_index = project_list.index(project_name)
#             project_type = project_types[project_index]
#             if project_type == 'Applied':
#                 output_file_applied.write(line + ',' + project_type + '\n')
#             else:
#                 output_file_tool.write(line + ',' + project_type + '\n')
#         else:
#             continue


# output_file_2= open('../CSV Output - New/Classification_JobFail_subtypes_class_1st_sub_add_NEW.csv', 'w+')
# output_file_2.write("file_name,TestFail,BuildError,TestError,CodeAnalysisError,TravisError,DeploymentError,RepoType\n")
#
# with open('../CSV Input - New/Classification_JobFail_subtypes_class_1st_sub_add.csv','r') as fileobj:
#     while (True):
#         line = fileobj.readline()
#         if not line:
#             break
#         file_path=line.split(',')[0]
#         line=line.replace('\n','')
#         if ('\\') not in file_path:
#             continue
#         project_name=file_path.split('\\')[7]
#         if project_name in project_list:
#             project_index=project_list.index(project_name)
#             project_type=project_types[project_index]
#             output_file_2.write(line + ',' + project_type + '\n')
#         else:
#             continue
#
#
# output_file_3= open('../CSV Output - New/Classification_JobFail_subtypes_class_subss_NEW.csv', 'w+')
# output_file_3.write("file_name,TestFail,BuildError,TestError,CodeAnalysisError,TravisError,DeploymentError,RepoType\n")
#
# with open('../CSV Input - New/Classification_JobFail_subtypes_class_subss.csv','r') as fileobj:
#     while (True):
#         line = fileobj.readline()
#         if not line:
#             break
#         file_path=line.split(',')[0]
#         line=line.replace('\n','')
#         if ('\\') not in file_path:
#             continue
#         project_name=file_path.split('\\')[7]
#         if project_name in project_list:
#             project_index=project_list.index(project_name)
#             project_type=project_types[project_index]
#             output_file_2.write(line + ',' + project_type + '\n')
#         else:
#             continue



