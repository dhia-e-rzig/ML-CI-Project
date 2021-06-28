from PythonScripts.Utils.Travis_Utils import get_travis_com_access, get_travis_org_access, \
    find_repos_in_travis_api_with_1_or_more_builds

set_travis=set()

find_repos_in_travis_api_with_1_or_more_builds(get_travis_com_access(), set_travis)
find_repos_in_travis_api_with_1_or_more_builds(get_travis_org_access(), set_travis)

f_applied = open('../../CSV Outputs/applied_travis_api_2.csv', 'w')
f_applied.write('ProjectName')
f_applied.write('\n')
for project in set_travis:
    f_applied.write(project)
    f_applied.write('\n')
