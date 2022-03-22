# Experimental, not currently used
#
# import pandas as pd
# import yaml
# from pprint import pprint
# import os
#
# import os
#
#
# df = pd.read_csv('../../CSV Inputs/api2_and_fs_projects_stats/travis_commit-history-05-11-21-11-29-19-applied.csv', sep=";")
#
# old_file_path=''
#
# for row in df.itertuples():
#     filepath=str(row[3])
#     if 'deleted' in str(filepath).lower():
#         continue
#     if filepath == old_file_path:
#         continue
#     try:
#         with open(filepath, 'r') as stream:
#             try:
#                 dicta= yaml.safe_load(stream)
#                 pprint(dicta['env'])
#                 # sp=dict['install']
#                 # sp=str(sp).replace("'",'')
#                 # sp=str(sp).replace("[",'')
#                 # sp=str(sp).replace("]",'')
#                 # os.popen("echo "+sp+">> 1.tmp")
#                 # stream = os.popen("shellcheck -s bash  -f gcc 1.tmp")
#                 # output = stream.read()
#                 # os.popen("del 1.tmp")
#                 # print(output)
#                 exit()
#             except yaml.YAMLError as exc:
#                 print(exc)
#     except Exception as e:
#         if type(e) == FileNotFoundError:
#             continue
#         else:
#             print(str(e))
#
