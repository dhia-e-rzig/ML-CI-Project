import pandas as pd

travis_applied_api2=pd.read_csv("CSV Inputs/Projects_sets/applied_travis_api_2.csv")
travis_tool_api2=pd.read_csv("CSV Inputs/Projects_sets/tool_travis_api_2.csv")
travis_applied_fs=pd.read_csv("CSV Inputs/Projects_sets/Applied_Travis_FS.csv")
travis_tool_fs=pd.read_csv("CSV Inputs/Projects_sets/Tool_Travis_FS.csv")

applied_api2_projects=list(travis_applied_api2['ProjectName'])
applied_fs_projects=list(travis_applied_fs['ProjectName'])

tool_api2_projects=list(travis_tool_api2['ProjectName'])
tool_fs_projects=list(travis_tool_fs['ProjectName'])

# applied_api1_only = [item for item in applied_fs_projects if item not in applied_api2_projects]
# print('Applied_Api1Only')
# print(len(applied_api1_only))
# applied_diff_api1_only=open("CSV Outputs/applied_api1_only.csv", 'w')
# applied_diff_api1_only.write("ProjectName")
# applied_diff_api1_only.write('\n')
# for project in applied_api1_only:
#     applied_diff_api1_only.write(project)
#     applied_diff_api1_only.write('\n')
#
# tool_api1_only = [item for item in tool_fs_projects if item not in tool_api2_projects]
# print('Tool_Api1Only')
# print(len(tool_api1_only))
#
# tool_diff_api1_only=open("CSV Outputs/tool_api1_only.csv", 'w')
# tool_diff_api1_only.write("ProjectName")
# tool_diff_api1_only.write('\n')
# for project in tool_api1_only:
#     tool_diff_api1_only.write(project)
#     tool_diff_api1_only.write('\n')
# tool_diff_fs_only=open("CSV Outputs/tool_fs_only.csv", 'w')
# tool_diff_fs_only.write("ProjectName")
# tool_diff_fs_only.write('\n')
#
# applied_diff_fs_only=open("CSV Outputs/applied_fs_only.csv", 'w')
# applied_diff_fs_only.write("ProjectName")
# applied_diff_fs_only.write('\n')

# tool_diff_fs_or_api=open("CSV Outputs/tool_fs_or_api.csv", 'w')
# tool_diff_fs_or_api.write("ProjectName")
# tool_diff_fs_or_api.write('\n')
#
# applied_diff_fs_or_api=open("CSV Outputs/applied_fs_or_api.csv", 'w')
# applied_diff_fs_or_api.write("ProjectName")
# applied_diff_fs_or_api.write('\n')
#

#
# applied_fs_only = [item for item in applied_api2_projects if item not in applied_api1_projects]
# for project in applied_fs_only:
#     applied_diff_fs_only.write(project)
#     applied_diff_fs_only.write('\n')
#
# applied_fs_or_api = set(applied_api1_projects + applied_api2_projects)
# for project in applied_fs_or_api:
#     applied_diff_fs_or_api.write(project)
#     applied_diff_fs_or_api.write('\n')

tool_diff_fs_and_api=open("CSV Outputs/tool_fs_and_api2.csv", 'w')
tool_diff_fs_and_api.write("ProjectName")
tool_diff_fs_and_api.write('\n')

applied_diff_fs_and_api=open("CSV Outputs/applied_fs_and_api2.csv", 'w')
applied_diff_fs_and_api.write("ProjectName")
applied_diff_fs_and_api.write('\n')

applied_fs_and_api = [item for item in applied_api2_projects if (item in applied_fs_projects)]
for project in applied_fs_and_api:
    applied_diff_fs_and_api.write(project)
    applied_diff_fs_and_api.write('\n')

tool_fs_and_api = [item for item in tool_api2_projects if (item in tool_fs_projects )]
for project in tool_fs_and_api:
    tool_diff_fs_and_api.write(project)
    tool_diff_fs_and_api.write('\n')
#
# tool_diff_fs_only=open("CSV Outputs/tool_diff_api_only.csv", 'w')
# tool_diff_fs_only.write("project,status")
# tool_diff_fs_only.write('\n')
#


#
# tool_fs_only = [item for item in tool_api2_projects if item not in tool_api1_projects]
# for project in tool_fs_only:
#     tool_diff_fs_only.write(project)
#     tool_diff_fs_only.write('\n')
#
# tool_fs_or_api = set(tool_api1_projects + tool_api2_projects)
# for project in tool_fs_or_api:
#     tool_diff_fs_or_api.write(project)
#     tool_diff_fs_or_api.write('\n')
#
# tool_fs_and_api = [item for item in tool_api2_projects if (item in tool_api1_projects and item in tool_api2_projects)]
# for project in tool_fs_and_api:
#     tool_diff_fs_and_api.write(project)
#     tool_diff_fs_and_api.write('\n')
# tool_diff_fs_only=open("CSV Outputs/tool_diff_api_only.csv", 'w')
# tool_diff_fs_only.write("project,status")
# tool_diff_fs_only.write('\n')
#
# applied_diff_fs_only=open("CSV Outputs/applied_diff_api_only.csv", 'w')
# applied_diff_fs_only.write("project,status")
# applied_diff_fs_only.write('\n')

# tool_fs_analysis = pd.read_csv("CSV Inputs/tool_fs_analysis.csv",error_bad_lines=False)
# tool_projects_fs_analysis=set(list(tool_fs_analysis['ProjectName']))
# for project in tool_api_only:
#     if project in tool_projects_fs_analysis:
#         tool_diff_anal.write(project+',found in FS analysis')
#         tool_diff_anal.write('\n')
#     else:
#         tool_diff_anal.write(project + ',not found locally')
#         tool_diff_anal.write('\n')
#
#
# applied_fs_analysis = pd.read_csv("CSV Inputs/applied_fs_analysis.csv",error_bad_lines=False)
# applied_projects_fs_analysis=set(list(applied_fs_analysis['ProjectName']))
#
# for project in applied_api1_only:
#     if project in applied_projects_fs_analysis:
#         applied_diff_anal.write(project+',found in FS analysis')
#         applied_diff_anal.write('\n')
#     else:
#         applied_diff_anal.write(project + ',not found locally')
#         applied_diff_anal.write('\n')
