import pandas as pd
import os

df_acc1=pd.read_csv('Set1-ManualLabeling.csv')
df_acc2=pd.read_csv('Set2-ManualLabeling.csv')
df_err=pd.read_csv('Set1-ManualLabeling-err.csv')
files_err = os.listdir('C:/Users/dhiarzig/Desktop/Research Projects/Summer 2021 paper - for MSR - Data/Replication Package 2.0/Randomly selected files - for  log analyzer/Errored logs - Set 1')
files_fail_1 = os.listdir('C:/Users/dhiarzig/Desktop/Research Projects/Summer 2021 paper - for MSR - Data/Replication Package 2.0/Randomly selected files - for  log analyzer/FailedLogs-Set 1')
files_fail_2 = os.listdir('C:/Users/dhiarzig/Desktop/Research Projects/Summer 2021 paper - for MSR - Data/Replication Package 2.0/Randomly selected files - for  log analyzer/FailedLogs-Set 2')
# print(files)
# exit()
log_files_list_1=df_acc1['file_name'].tolist()

log_files_list_2=df_acc2['file_name'].tolist()

# log_files_err=df_err['file_name'].tolist()

file_list_with_path_1=[]
file_list_with_path_2=[]
file_list_with_path_err=[]

path_set_1=set()
path_set_2=set()
path_set_err=set()


for path, folders, files in os.walk('D:/ML-CI/Project Stats Year'):
    for file in files:
        if file in files_fail_1:
            file_list_with_path_1.append(os.path.join(path, file))
            files_fail_1.remove(file)
            path_set_1.add(path)
        elif file in files_fail_2:
            file_list_with_path_2.append(os.path.join(path, file))
            files_fail_2.remove(file)
            path_set_2.add(path)
        elif file in files_err:
            file_list_with_path_err.append(os.path.join(path, file))
            files_err.remove(file)
            path_set_err.add(path)
        else:
            continue


print(file_list_with_path_1)
print(str(file_list_with_path_2).replace(',',';'))
print(str(file_list_with_path_err).replace(',',';'))


print(log_files_list_2)
print(len(file_list_with_path_1))
print(len(file_list_with_path_2))
print(len(file_list_with_path_err))


print(path_set_1)
print((path_set_2))
print(path_set_err)

print(len(path_set_1))
print(len(path_set_2))
print(len(path_set_err))

print(len(files_fail_1))
print(len(files_fail_2))
print(len(files_err))
