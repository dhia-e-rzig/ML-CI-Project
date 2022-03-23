import re
import os
from PythonScripts.Utils import Github_Utils as GHU
import pandas as pd
from github import Github
import wget
import multiprocessing as mp
from os import path

NOTCI = 'NOTCI'

with open("../../CSV Inputs/ConfigFiles_for_CI_tool_detection.xlsx","rb") as configFile:
    special_files_dataframe=pd.read_excel(configFile)

temp_list=special_files_dataframe["Tool"].tolist()
Tools_list=res = [i for n, i in enumerate(temp_list) if i not in temp_list[:n]]
Directories = special_files_dataframe["Directory"].tolist()
FileNamesAndExtensions = special_files_dataframe["Files"].tolist()
FileNamesAndExtensionsAndDirectories = list(zip(FileNamesAndExtensions, Directories))


# tools_and_files_tups=tools_and_files[tools_and_files['Category']=="Continuous Integration"] [['Tool','Files']].values.tolist()
g=Github(GHU.get_github_token())


generic_ext = ['.csv', '.py', '.java', '.c', '.cpp', '.exe', '.cs', '.md', '.txt','.html','.ts','.go','.png','.js','.css','.s','.ini','.jpg','.bmp','ipynb','.map','.scss','.gif','.markdown','.pem','.sh','.xaml','.csproj','.onnx','.svg','.lock','.sln','.pdf','.resx','.tdb','.log','.p','.pbtxt',".xaml",'.tsv','.bmp','.h',".pt",'.pyc',".xml",'.yaml','.yml']
ignored_ext=['.gitignore', 'README.md', 'LICENSE', "AUTHORS", "CONTRIBUTORS", "PATENTS", "OWNERS", "SECURITY_CONTACTS", "NOTICE", "Readme", ".DS_Store", ".gitattributes", "CODEOWNERS", ".gitkeep", ".gitmodules", "GOLANG_CONTRIBUTORS"]


class ci_local_fs_finder():
    def __init__(self, full_name):
        self.full_name = full_name


    def find_ci_local(self):
        print('Processing '+self.full_name)
        try:
            allpath='/media/umd-002677/TOSHIBA EXT/PhD Work/repos/no-ai-ml'
            if path.exists(allpath+'/'+self.full_name):
                dirpath=allpath+'/'+self.full_name
            else:

                print (self.full_name+' ProjectNotFound')
                return (self.full_name,'ProjectNotFound')
            tools_set=set()
            for root, dirs, files in os.walk(dirpath):
                for file in files:

                    if '.travis.yml' == str(file).lower():
                        result_temp=find_easeml_ci(root,file)
                        if result_temp != ('%s' % NOTCI):
                            tools_set.add(result_temp)
                    result_temp=classify_file(root,file)
                    if result_temp != ('%s' % NOTCI):
                        tools_set.add(result_temp)
            return (self.full_name,tools_set)
        except Exception as e:
            print(self.full_name+' '+ e.__str__() )
            return (self.full_name,'Exception',str(e))




def find_easeml_ci(dirpath, filename):
    easeML_found=False
    try:
        pattern=r'^ML:'
        with open(dirpath+'/'+filename, 'r') as file_obj:
            Lines = file_obj.readlines()
            for line in Lines:
                if re.compile(pattern).search(line):
                    easeML_found=True
                    return 'easeml'
    except Exception as e:
        print('Unknown exception: ' + str(e))
    return NOTCI

def classify_file(dirpath, filename):
    filename = str(filename).strip()
    for iext in ignored_ext:
        if filename==iext:
            return
    for i in range(0, len(FileNamesAndExtensionsAndDirectories)):
        (ext, dir) = FileNamesAndExtensionsAndDirectories[i]
        if isinstance(dir, str):
            if dir !='NA' and dir.lower() not in dirpath.lower():
                continue
        if(len(ext) <= 6):
            if filename.lower().endswith(ext.lower()):
                tool = str(special_files_dataframe.loc[(special_files_dataframe['Files'] == ext) & (special_files_dataframe['Directory'] == dir) ]['Tool'].values).replace('[', '').replace(']', '').replace('\'','')
                return tool

        else:
            if '*' == ext :
                tool = str(special_files_dataframe.loc[(special_files_dataframe['Files'] == ext) &( special_files_dataframe['Directory'] == dir ) ]['Tool'].values).replace(
                    '[', '').replace(']', '').replace('\'', '')

                return tool
            elif '*' in ext :
                arr = ext.split('*')
                if filename.lower().startswith(arr[0]) and filename.lower().endswith(arr[1]):
                    tool =  str(special_files_dataframe.loc[(special_files_dataframe['Files'] == ext) &( special_files_dataframe['Directory'] == dir ) ]['Tool'].values).replace(
                    '[', '').replace(']', '').replace('\'', '')
                    return tool
            elif filename.lower() == ext.lower() or "."+filename.lower() == ext.lower() or filename.lower() == "."+ext.lower():

                tool =  str(special_files_dataframe.loc[(special_files_dataframe['Files'] == ext) &( special_files_dataframe['Directory'] == dir ) ]['Tool'].values).replace(
                    '[', '').replace(']', '').replace('\'', '')

                return tool
    return NOTCI


def worker(arg):
    obj= arg
    return obj.find_ci_local()

NUM_CORE = mp.cpu_count()


f_out = open('CI_adoption_nonml.csv','w+',encoding='utf-8')
err_out = open('CI_adoption_nonml_errors.csv','w+',encoding='utf-8')
f_out.write("projectName,AppVeyor,Azure,BuildBot,CircleCI,CloudBuild,CodeBuild,GitLab,Jenkins,Travis,VSTSCI,GithubA,easeML")
f_out.write('\n')


if __name__ == "__main__":
    df_non_ml=pd.read_csv('../../CSV Input - New/NonML-classification.csv')
    list_of_objects =[ci_local_fs_finder(el) for el in df_non_ml['ProjectName'].tolist()]
    print(len(list_of_objects))
    pool = mp.Pool(NUM_CORE)
    list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()
    for res in list_of_results:
        project_name=res[0]
        if(res[1] == 'ProjectNotFound'):
            err_out.write('Project Not found '+ project_name+'\n')
        if (res[1] == 'Exception'):
            err_out.write('Project encountered exception ' + project_name+','+res[2])
        tools_found=res[1]
        AppVeyor = False
        Azure = False
        BuildBot = False
        CircleCI = False
        CloudBuild = False
        CodeBuild = False
        GitLab = False
        Jenkins = False
        VSTSCI = False
        Travis = False
        GithubA = False
        easeML = False
        if len(tools_found)>0 :
            if 'AppVeyor' in tools_found:
                AppVeyor=True
            if 'Azure Pipeline' in tools_found:
                Azure=True
            if 'BuildBot' in tools_found:
                BuildBot=True
            if 'CircleCI' in tools_found:
                CircleCI=True
            if 'CloudBuild' in tools_found:
                CloudBuild=True
            if 'CodeBuild' in tools_found:
                CodeBuild=True
            if 'GitLab Ci' in tools_found:
                GitLab=True
            if 'Jenkins' in tools_found:
                Jenkins=True
            if 'Travis' in tools_found:
                Travis=True
            if 'VSTSCI' in tools_found:
                VSTSCI=True
            if 'Github Actions' in tools_found:
                GithubA=True
            if 'easeml' in tools_found:
                easeML=True
        f_out.write(project_name+','+str(AppVeyor)+','+str(Azure)+','+str(BuildBot)+','+str(CircleCI)+','+str(CloudBuild)+','+str(CodeBuild)+','+str(GitLab)+','+str(Jenkins)+','+str(Travis)+','+str(VSTSCI)+','+str(GithubA)+','+str(easeML))
        f_out.write('\n')


