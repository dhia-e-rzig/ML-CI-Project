import pandas as pd


# python_non_ml_df=pd.read_csv('non-ml_repos_langs-python-only-03-15-22-12-33-39.csv',sep=';')
travis_api_non_ml_df=pd.read_csv('/home/umd-002677/PycharmProjects/ML-CI/CSV Archives/Ci Adoption folder/travis-adoption-nonml.csv')
# ci_fs_nonml=pd.read_csv('CI_adoption_nonml-backup.csv')
# ci_fs_github_nonml=pd.read_csv('CI_adoption_nonml-githubactions.csv')
github_api_nonml=pd.read_csv('/home/umd-002677/PycharmProjects/ML-CI/CSV Archives/Ci Adoption folder/githubActions_stats_nonml.csv')
#
travis_api_non_ml_df = travis_api_non_ml_df.loc[travis_api_non_ml_df['TravisAPIAdoption'] == True]
travis_api_non_ml=travis_api_non_ml_df['ProjectName'].tolist()

# print('travis_api_non_ml')
# print(len(travis_api_non_ml))
github_api_non_ml_df = github_api_nonml.loc[github_api_nonml['TotalRuns'] > 0]
github_api_non_ml=github_api_non_ml_df['ProjectName'].tolist()

# print('github_api_non_ml')
# print(len(github_api_non_ml))
#
# travis_fs_nonml=ci_fs_nonml.loc[ci_fs_nonml['Travis'] == True]
# github_fs_nonml=ci_fs_github_nonml.loc[ci_fs_github_nonml['GithubA'] == True]
# print('github_fs_nonml')
# print(len(github_fs_nonml))
#
# nonml_python_and_travis_api = [item for item in python_non_ml_df['RepoName'].tolist() if (item in travis_api_non_ml['ProjectName'].tolist())]
# nonml_python_and_travis_api_and_fs = [item for item in  nonml_python_and_travis_api if (item in travis_fs_nonml['projectName'].tolist())]
# RQ3_4_addition=nonml_python_and_travis_api
# # f_out=open('RQ3_4_NonML.csv','w+')
# # f_out.write('RepoName,RepoType,GitHubURL\n')
# # for project in RQ3_4_addition:
# #     f_out.write(project+',NonML,https://github.com/'+project+'.git'+'\n')
#
# RQ2_addition=nonml_python_and_travis_api_and_fs
# # f_out=open('RQ2_NonML.csv','w+')
# # f_out.write('RepoName,RepoType,GitHubURL'+'\n')
# # for project in RQ2_addition:
# #     f_out.write(project+',NonML,https://github.com/'+project+'.git'+'\n')
#
#
#
# nonml_python_and_github_api = [item for item in python_non_ml_df['RepoName'].tolist() if (item in github_api_non_ml['ProjectName'].tolist())]
# nonml_python_and_github_api_and_fs = [item for item in  nonml_python_and_github_api if (item in github_fs_nonml['projectName'].tolist())]
#
# nonml_github_fs_and_github_api = [item for item in github_api_non_ml['ProjectName'].tolist() if (item in github_fs_nonml['projectName'].tolist())]
# print('nonml_github_fs_and_github_api')
# print(len(nonml_github_fs_and_github_api))
#
#
# nonml_travis_fs_and_travis_api = [item for item in travis_api_non_ml['ProjectName'].tolist() if (item in travis_fs_nonml['projectName'].tolist())]
# print('nonml_travis_fs_and_travis_api')
# print(len(nonml_travis_fs_and_travis_api))
#
#
# print('nonml_python_and_travis_api')
# print(len(nonml_python_and_travis_api))
# print('nonml_python_and_travis_api_and_fs')
# print(len(nonml_python_and_travis_api_and_fs))
#
#
# print('nonml_github_fs_and_github_api')
# print(len(nonml_github_fs_and_github_api))
#
# print('nonml_python_and_github_api')
# print(len(nonml_python_and_github_api))
# print('nonml_python_and_github_api_and_fs')
# print(len(nonml_python_and_github_api_and_fs))
nonml_githubortravisapi= set(travis_api_non_ml+github_api_non_ml)

print('nonml_githubortravisapi')
print(len(nonml_githubortravisapi))