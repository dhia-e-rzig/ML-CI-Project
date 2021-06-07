from PyTravisCI import defaults, TravisCI
import pandas as pd


travis_access_com = TravisCI(access_token="yY5Pnt7Mgec81-8mAWc2aQ", access_point=defaults.access_points.PRIVATE)
travis_access_org = TravisCI(access_token="bYlcgiscf4elZlPEn8zlaQ")


def find_repos_in_travis_api(travis):
    f_applied= open('CSV Outputs/applied_travis_api.csv', 'w')
    f_applied.write('ProjectName')
    f_applied.write('\n')
    # f_tool = open('CSV Outputs/tool_travis_api.csv', 'w')
    # f_tool.write('ProjectName')
    # f_tool.write('\n')
    f_errors = open('CSV Outputs/errors_travis_api.csv', 'w')
    f_errors.write('ProjectName,Exception')
    f_errors.write('\n')

    try :
        df_applied=pd.read_csv("CSV Inputs/AppliedProjects_all.csv")
        # df_tool=pd.read_csv("CSV Inputs/ToolProjects_all.csv")
        applied_projects=list(df_applied["ProjectName"])
        # tool_projects=list(df_tool["ProjectName"])
        for project_name in applied_projects:
            try:
                travis_repo = travis.get_repository(project_name)
                f_applied.write(project_name)
                f_applied.write('\n')
                print(project_name)
            except Exception as e:
                print(str(e))
                if 'not_found' not in str(e):
                    row=project_name+','+str(e)
                    f_errors.write(row)
                    f_errors.write('\n')
                    print(row)
                continue
        # for project_name in tool_projects:
        #     try:
        #         travis_repo = travis.get_repository(project_name)
        #         f_tool.write(project_name)
        #         f_tool.write('\n')
        #         print(project_name)
        #     except Exception as e:
        #         print(str(e))
        #         if 'not_found' not in str(e):
        #             row = project_name + ',' + str(e)
        #             f_errors.write(row)
        #             f_errors.write('\n')
        #             print(row)
        #         continue
    except Exception as e:
        print('CSV file access problem')
        print(str(e))



set_travis=set()

def find_repos_in_travis_api_with_1_or_more_builds(travis,set):

    # f_tool = open('CSV Outputs/tool_travis_api.csv', 'w')
    # f_tool.write('ProjectName')
    # f_tool.write('\n')
    f_errors = open('CSV Outputs/errors_travis_api.csv', 'w')
    f_errors.write('ProjectName,Exception')
    f_errors.write('\n')
    try :
        df_applied=pd.read_csv("CSV Inputs/AppliedProjects_all.csv")
        # df_tool=pd.read_csv("CSV Inputs/ToolProjects_all.csv")
        # applied_projects=list(df_applied["ProjectName"])
        tool_projects=list(df_applied["ProjectName"])
        for project_name in tool_projects:
            # project_name="ternaus/robot-surgery-segmentation"
            try:
                travis_repo = travis.get_repository(project_name)
                if travis_repo is None:
                    continue
                list_of_builds =travis_repo.get_builds()
                if list_of_builds is None:
                    continue
                # for branch in list_of_branches:
                #     if branch['last_build'] is not None:
                #         has_builds=True
                #         break

                if len(list_of_builds.dict())>0:
                    set.add(project_name)
                    print(project_name)
            except Exception as e:
                print(str(e))
                if 'not_found' not in str(e):
                    row=project_name+','+str(e)
                    f_errors.write(row)
                    f_errors.write('\n')
                    print(row)
                continue
    except Exception as e:
        print('CSV file access problem')
        print(str(e))


find_repos_in_travis_api_with_1_or_more_builds(travis_access_com,set_travis)
find_repos_in_travis_api_with_1_or_more_builds(travis_access_org,set_travis)

f_applied = open('CSV Outputs/applied_travis_api_2.csv', 'w')
f_applied.write('ProjectName')
f_applied.write('\n')
for project in set_travis:
    f_applied.write(project)
    f_applied.write('\n')
