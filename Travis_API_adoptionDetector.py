from PyTravisCI import TravisCI
import pandas as pd


travis_access = TravisCI(access_token="bYlcgiscf4elZlPEn8zlaQ")


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
        df_tool=pd.read_csv("CSV Inputs/ToolProjects_all.csv")
        applied_projects=list(df_applied["ProjectName"])
        tool_projects=list(df_tool["ProjectName"])
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

find_repos_in_travis_api(travis_access)