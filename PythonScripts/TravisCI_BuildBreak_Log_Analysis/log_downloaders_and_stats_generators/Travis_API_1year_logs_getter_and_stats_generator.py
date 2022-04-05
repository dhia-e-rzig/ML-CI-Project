import datetime

import PyTravisCI
import pandas as pd
from PythonScripts.Utils import Travis_Utils
df_nonml=pd.read_csv('../../../CSV Input - New/RQ3_4_NonML.csv')
df_ml=pd.read_csv('../../../CSV Input - New/RQ3-RQ4-new.csv')
import os
import sys
from datetime import datetime, date, time, timedelta

import shutil

# List_of_tool_repos=df.loc[df['RepoType']=='Tool']['RepoName'].to_list()
List_of_nonml_repos=df_nonml['RepoName'].tolist()
List_of_ml_repos=df_ml['RepoName'].tolist()
# List_of_applied_repos=df.loc[df['RepoType']=='Applied']['RepoName'].to_list()


class Project_State_Processor_class():
    def __init__(self, project,type):
        self.project = project
        self.type = type
        self.result = ""

    def find_project_rates_between_dates(self):
        start_time_all = time.perf_counter()
        project=self.project
        cutoff=date(2021,8,12)
        # cutoff=date(2021,8,12)
        # script_path = os.path.realpath(__file__)
        script_path='../../../Project Stats Year'
        project_folder_path = os.path.join(script_path, str(self.type)+'/' + project.replace('/', '_',1))
        if os.path.exists(project_folder_path):
            shutil.rmtree(project_folder_path)

        project_job_logs_folder_path=os.path.join(script_path, str(self.type)+'/' + project.replace('/', '_',1)+'/job_logs')
        if not os.path.exists(project_folder_path):
            os.makedirs(project_folder_path)

        if not os.path.exists(project_job_logs_folder_path):
            os.mkdir(project_job_logs_folder_path)

        project_csv_build = open(project_folder_path+'/' + 'build_detailed_info.csv', 'w+')
        project_csv_build.write('BuildID,BuildCreationDate,BuildState,BuildDuration')
        project_csv_build.write('\n')
        project_csv_jobs = open(project_folder_path + '/' + 'job_detailed_info.csv', 'w+')
        project_csv_jobs.write('JobID,JobCreationDate,JobState,JobFinishedAt,JobDuration')
        project_csv_jobs.write('\n')
        try:
            travis_repo = Travis_Utils.get_travis_repo(project)
        except:
            print(project+" Not found")
            project_csv_build.write('ProjectNotFound')
            project_csv_build.write('\n')
            project_csv_jobs.write('ProjectNotFound')
            project_csv_jobs.write('\n')
            with open("travis_api_succes_rates_err_v2.txt", "a+") as error:
                error.write(project+" Not found \n")
            return (self.project,self.type)
        try:

            # try:
            #     build_page = travis_repo.get_builds(params = {'sort_by': 'started_at:desc'})
            # except:
            build_page=travis_repo.get_builds()
            if(build_page is None ) or build_page.builds is None:
                return
            bool_build_next_page =  build_page.has_next_page()
            if build_page is None or build_page.builds is None:
                return
            last_build=build_page.builds[0]

            while last_build.started_at is None or last_build.started_at.date() > cutoff:
                i = len(build_page.builds) - 1
                while (i > -1) and (last_build.started_at is None or last_build.started_at.date() > cutoff):
                    last_build = build_page.builds[i]
                    i = i - 1
                bool_build_next_page = build_page.has_next_page()
                if (bool_build_next_page and (last_build.started_at is None or last_build.started_at.date() > cutoff)):
                    build_page = build_page.next_page()
                elif (not bool_build_next_page) and (
                        last_build.started_at is None or last_build.started_at.date() > cutoff):
                    break
            if (last_build.started_at is None or last_build.started_at.date() > cutoff):
                print('oldest before cutoff not found ' + self.project)
                return

            date_end = last_build.started_at.date()+timedelta(days=1)
            print(date_end)
            date_beg = date_end - timedelta(days=366)
            dates_csv=open(project_folder_path + '/' + 'dates.csv', 'w+')
            dates_csv.write(str(date_beg))
            dates_csv.write('\n')
            dates_csv.write(str(date_end))
            dates_csv.write('\n')
            dates_csv.flush()
            bool_build_next_page=True
            while (bool_build_next_page):
                bool_build_next_page = build_page.has_next_page()
                if build_page is None or build_page.builds is None:
                    return
                oldest_build_on_page = build_page.builds[-1]

                i = len(build_page.builds) - 1
                while (oldest_build_on_page.started_at is None and i > -1):
                    oldest_build_on_page = build_page.builds[i]
                    i = i - 1

                # if (i == -1):
                #     return
                if (oldest_build_on_page.started_at is  None and  build_page.has_next_page()):
                    build_page = build_page.next_page()
                    bool_build_next_page = build_page.has_next_page()
                    continue
                if (oldest_build_on_page.started_at.date() > date_end and  build_page.has_next_page()):
                    build_page = build_page.next_page()
                    bool_build_next_page = build_page.has_next_page()
                    continue
                if build_page is None or build_page.builds is None:
                    return
                newest_build_on_page = build_page.builds[0]
                i = 1
                while (newest_build_on_page.started_at is None and i < len(build_page.builds)):
                    newest_build_on_page = build_page.builds[i]
                    i = i+1
                if (i == len(build_page.builds)):
                    return
                if (newest_build_on_page.started_at.date() < date_beg):
                    return
                if build_page is None or build_page.builds is None:
                    return

                for build in build_page.builds:
                    # print(build)
                    try:
                        if(build.started_at is None):
                            continue
                        if(build.started_at.date()> date_end):
                            continue
                        if(build.started_at.date()<date_beg):
                            return
                        print(str(project)+','+str(build.id) + ',' + str(build.started_at.date()) + ',' + str(build.state) + ',' + str(build.duration))
                        project_csv_build.write(
                            str(build.id) + ',' + str(build.started_at.date()) + ',' + str(build.state) + ',' + str(build.duration))
                        project_csv_build.write('\n')
                        jobs=build.get_jobs()
                        if jobs is None:
                            continue
                        for job in jobs:
                            if job.finished_at is None:
                                job_finished_date="None"
                            else:
                                job_finished_date=job.finished_at.date()
                            if job.started_at is None:
                                job_started_date="None"
                            else:
                                job_started_date=job.started_at.date()
                            if job_started_date != "None" and job_finished_date != "None":
                                duration=(job_finished_date-job_started_date).total_seconds()
                                duration=int(duration)
                            else:
                                duration='None'
                            project_csv_jobs.write(
                                str(job.id) + ',' + str(job_started_date) + ',' + str(job.state) + ',' + str(
                                    job_finished_date)+','+str(duration))
                            project_csv_jobs.write('\n')
                            if (job.is_errored(sync=True)) or (job.is_failed(sync=True)):
                                try:
                                    output_str = job.get_log().content
                                except:
                                    output_str="Log Not Found"
                                if (output_str == "" or output_str is None):
                                    output_str="Empty Log"
                                with open(project_job_logs_folder_path + '/' + str(job.id) + '.txt', 'w+',
                                          encoding='utf-8') as file:
                                    file.write(output_str)
                    except Exception as e:
                        with open("travis_api_succes_rates_err_v2.txt", "a+") as error:
                            error.write(project +',buildID'+str(build.id)+',' + str(e))
                            error.write('\n')
                            print(project +'buildID'+str(build.id)+' ' + str(e))
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            print(exc_type, fname, exc_tb.tb_lineno)
                if build_page is None:
                    return
                if build_page.has_next_page() is None or build_page.has_next_page() is False:
                    return
                try:
                    print(build_page.has_next_page())
                    build_page = build_page.next_page()
                except Exception as e:
                    with open("travis_api_succes_rates_err_v2.txt", "a+") as error:
                        error.write(project + ',buildID' + '00' + ',' + str(e))
                        error.write('\n')
                        print(project + 'buildID' +'00' + ' ' + str(e))
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        print(exc_type, fname, exc_tb.tb_lineno)
                    return
        except Exception as e:
            with open("travis_api_succes_rates_err_v2.txt","a+") as error:
                error.write(project+' '+str(e))
                error.write('\n')
                print(project+' '+str(e))
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)

        end_time_all = time.perf_counter()
        print("Execution Time for "+project+f" : {end_time_all - start_time_all:0.6f}")
import multiprocessing as mp
NUM_CORE = mp.cpu_count()
import time

def worker(arg):
    obj= arg
    return obj.find_project_rates_between_dates()

if __name__ == "__main__":
    start_time_all = time.perf_counter()
    # print('starting NonML')
    # # log_files = os.listdir('FailedLogs-ForTesting')
    # list_of_objects = [Project_State_Processor_class(i,'NonML') for i in List_of_nonml_repos]
    # pool = mp.Pool(NUM_CORE)
    # list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    # pool.close()
    # pool.join()
    # end_time_all = time.perf_counter()
    # print(f"Execution Time for NonML : {end_time_all - start_time_all:0.6f}")

    # start_time_all = time.perf_counter()
    # print('starting ML')
    # log_files = os.listdir('FailedLogs-ForTesting')


    # list_applied=['vgrabovets/multi_rake','PrincetonUniversity/ASPIRE-Python','anrputina/outlierdenstream','priyankshah7/hypers','IBM/MAX-Audio-Sample-Generator','ncbi-nlp/NegBio','proycon/gecco','a-slide/pycoQC','dlebech/lyrics-generator','ssydasheng/GPflow-Slim','textpipe/textpipe','Hananel-Hazan/bindsnet','AmeyaWagh/Traffic_sign_detection_YOLO','nerox8664/gluon2pytorch','cosanlab/nltools']
    # list_tool=['geomstats/geomstats','stanfordnlp/stanfordnlp','pytorch/vision','scikit-multiflow/scikit-multiflow','snipsco/snips-nlu','microsoft/MMdnn','PaddlePaddle/X2Paddle','openml/automlbenchmark']
    # list_nonml=['cemoody/lda2vec','dshearer/jobber','eudicots/Cactus','ezaquarii/vpn-at-home','jacksu/utils4s','jameysharp/corrode','jazzband/django-admin2','mjhea0/flaskr-tdd','nvdv/vprof','peterbraden/node-opencv','phonegap/phonegap-app-desktop','pymc-devs/pymc','rcaloras/bashhub-client','retspen/webvirtmgr','rmax/scrapy-redis','rs/pushd','saghul/pyuv','samgiles/slumber','satori-com/tcpkali','scanmem/scanmem','scoder/lupa','sdiehl/write-you-a-haskell','seb-m/pyinotify','sebleier/django-redis-cache','serverdensity/python-daemon','sripathikrishnan/redis-rdb-tools','tdryer/hangups','ukdtom/WebTools.bundle','ustream/openduty','vektah/CodeGlance','viewflow/django-fsm','wesm/feather','wummel/linkchecker','yougov/mongo-connector ']
    # list_nonml=['SilenceIM/Silence','SirVer/ultisnips','brave/browser-laptop','cmu-db/peloton','codesenberg/bombardier','dropbox/godropbox','flaskbb/flaskbb','flexxui/flexx','flyimg/flyimg','ionelmc/pytest-benchmark','mila-iqia/blocks','numenta/nupic','openai/roboschool','pybuilder/pybuilder','pythonprofilers/memory_profiler','rholder/retrying','riptano/ccm','sfzhang15/RefineDet']

    #list_applied=['ParrotPrediction/pyalcs',' textpipe/textpipe',' wkentaro/chainer-cyclegan',' shineware/PyKOMORAN',' deepfakes/faceswap']
    list_tool=['cgre-aachen/bayseg','explosion/spaCy','joeylitalien/noise2noise-pytorch','biolab/orange3','openml/automlbenchmark']

    start_time_all = time.perf_counter()
    print('starting Tool')
    list_of_objects = [Project_State_Processor_class(str(el),'Tool') for el in list_tool]
    pool = mp.Pool(2)
    list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()
    print('running repeat')
    list_of_objects = [Project_State_Processor_class(x[0], x[1]) for x in list_of_results if x is not None]
    pool = mp.Pool(2)
    list_of_results = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()
    repeat_list = []
    end_time_all = time.perf_counter()
    print(f"Execution Time for Tool : {end_time_all - start_time_all:0.6f}")

    list_applied=['textpipe/textpipe','wkentaro/chainer-cyclegan','shineware/PyKOMORAN','deepfakes/faceswap','fsx950223/mobilenetv2-yolov3','Ha0Tang/SelectionGAN','xvjiarui/GCNet','felixgwu/img_classification_pk_pytorch']
    # list_tool=['cgre-aachen/bayseg,explosion/spaCy,RasaHQ/rasa_core,DigitalSlideArchive/HistomicsTK']
    start_time_all = time.perf_counter()
    print('starting Applied')
    list_of_objects = [Project_State_Processor_class(str(el),'Applied') for el in list_applied]
    pool = mp.Pool(2)
    list_of_results_2 = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()
    print('running repeat')
    list_of_objects = [Project_State_Processor_class(x[0], x[1]) for x in list_of_results_2 if x is not None]
    pool = mp.Pool(2)
    list_of_results_2 = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()

    end_time_all = time.perf_counter()
    print(f"Execution Time for Applied : {end_time_all - start_time_all:0.6f}")

    list_nonml = ['khamidou/kite','olgabot/prettyplotlib','pimusicbox/pimusicbox','pymc-devs/pymc']
    # list_tool=['cgre-aachen/bayseg,explosion/spaCy,RasaHQ/rasa_core,DigitalSlideArchive/HistomicsTK']
    start_time_all = time.perf_counter()
    print('starting NonML')
    list_of_objects = [Project_State_Processor_class(str(el), 'NonML') for el in list_nonml]
    pool = mp.Pool(2)
    list_of_results_2 = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()
    print('running repeat')
    list_of_objects = [Project_State_Processor_class(x[0], x[1]) for x in list_of_results_2 if x is not None]
    pool = mp.Pool(2)
    list_of_results_2 = pool.map(worker, ((obj) for obj in list_of_objects))
    pool.close()
    pool.join()

    end_time_all = time.perf_counter()
    print(f"Execution Time for NonML : {end_time_all - start_time_all:0.6f}")

    # pr = Project_State_Processor_class("adhaamehab_arabicnlp","Applied")
    # pr.find_project_rates_between_dates()
