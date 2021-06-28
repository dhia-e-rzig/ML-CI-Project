import pandas as pd
from PyTravisCI import defaults, TravisCI

def get_travis_com_access():
    travis_access_com = TravisCI(access_token="yY5Pnt7Mgec81-8mAWc2aQ", access_point=defaults.access_points.PRIVATE)
    return travis_access_com


def get_travis_org_access():
    travis_access_org = TravisCI(access_token="bYlcgiscf4elZlPEn8zlaQ")
    return travis_access_org


def get_travis_repo(repo_name):
        try:
            travis_repo = get_travis_com_access().get_repository(repo_name)
            list_of_builds = travis_repo.get_builds().builds
            if list_of_builds is None or len(list_of_builds)==0:
              raise Exception
        except:
            try:
                travis_repo=get_travis_org_access().get_repository(repo_name)
                list_of_builds = travis_repo.get_builds().builds
                if list_of_builds is None or len(list_of_builds)==0:
                    raise Exception
            except Exception as e:
                raise e
        return travis_repo


def get_travis_job_repo(job_id):
        try:
            travis_job= get_travis_com_access().get_job(job_id)
            travis_repo = travis_job.repository
            login = str(travis_job.owner.login)
            name = str(travis_repo.name)
            travis_repo_full_name = login + '/' + name
        except:
            try:
                travis_job = get_travis_org_access().get_job(job_id)
                travis_repo = travis_job.repository
                login = str(travis_job.owner.login)
                name = str(travis_repo.name)
                travis_repo_full_name = login + '/' + name
            except Exception as e:
                raise e
        return travis_repo_full_name

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
    except Exception as e:
        print('CSV file access problem')
        print(str(e))
