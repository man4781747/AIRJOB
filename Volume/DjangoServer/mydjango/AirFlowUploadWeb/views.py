from django.shortcuts import render
from django.http import JsonResponse
from django.utils.decorators import method_decorator 
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import FileResponse  
from django.http import QueryDict
import re
import time
import sys
import os
import json
sys.path.append(os.path.split(os.path.realpath(__file__))[0])
import connectAirflow
import dagSettingFileManager as dagFile
import datetime
import zipfile
import shutil

airflowConnecter = connectAirflow.airflowConnecter(
    'TestAccount@gmail.com',
    'password',
    'http://airflow:8080'
)

S_dagsFolderPath = r'/airflowDagsFolder/dagBuilder'
S_dagsDeletedPath = r'/deletedDag'
S_tarFolder = r'/tarFolder'
if not os.path.exists(S_tarFolder):
    os.makedirs(S_tarFolder)
if not os.path.exists(S_dagsDeletedPath):
    os.makedirs(S_dagsDeletedPath)

@csrf_protect
def mainHTML(request):
    return render(request, 'MainHTML.html')

@csrf_protect
def Airflow_ProjectManager_HTML(request):
    return render(request, 'Airflow_ProjectManager.html')

@csrf_protect
def testHTML(request, groupName):
    S_groupPath = os.path.join(S_dagsFolderPath, groupName)
    if os.path.exists(S_groupPath):
        return render(request, 'MainHTML.html')
    else:
        return render(request, 'ProjectDonotExists.html')

def SearchFolder(S_folderPath):
    D_folderInfo = {
        'folderName': os.path.split(S_folderPath)[-1],
        'fullPath': S_folderPath,
        'files' : {},
        'folders' : {},
        'WTF' : {},
    }

    if not os.path.exists(S_folderPath):
        return D_folderInfo


    L_listdir = os.listdir(S_folderPath)
    for S_itemName in L_listdir:
        S_fullPath = os.path.join(S_folderPath, S_itemName)
        
        
        
        if os.path.isfile(S_fullPath) and os.path.splitext(S_itemName)[-1].lower()=='.py':
            Obj_fileStat = os.stat(S_fullPath)
            D_folderInfo['files'][S_itemName] = {
                'fullPath' : S_fullPath,
                'Type' : os.path.splitext(S_itemName)[-1],
                'Size' : Obj_fileStat.st_size,
                'LastModified' : datetime.datetime.fromtimestamp(Obj_fileStat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            }
        # elif os.path.isdir(S_fullPath):
        #     D_folderInfo['folders'][S_itemName] = SearchFolder(S_fullPath)
            
        else:
            D_folderInfo['WTF'][S_itemName] = {
                'fullPath' : S_fullPath,
            }
            
    return D_folderInfo

# Create your views here.
def test(request):
    return JsonResponse({'AllPicDate':[1,2,3]})
    
def MainWeb(request):
    return render(request, 'MainHTML.html', {})

@method_decorator(csrf_exempt)
def UploadAttachFile_v1(request, groupName, dagID):
    # time.sleep(5)
    if request.method == 'POST':  
        try:
            S_dagAttachFilesFolder = os.path.join(S_dagsFolderPath, groupName, dagID,'UploadedFile')
            S_filePath = os.path.join(S_dagAttachFilesFolder, request.POST['fileName']) 
            if not os.path.exists(S_dagAttachFilesFolder):
                os.makedirs(S_dagAttachFilesFolder)
            
            with open(S_filePath, 'wb') as f:
                for chunk in request.FILES['fileUploaded'].chunks():
                    f.write(chunk)
            # time.sleep(2)
            return JsonResponse({
                    'Result': 'Success',
                    'message': '',
                    'fileKey':request.POST['fileKey']
                })        
        except Exception as e:
            # time.sleep(2)
            return JsonResponse({
                'result': 'Fail',
                'message': str(e),
                'fileKey':request.POST['fileKey']
                })       
    return JsonResponse({'AllPicDate':[1,2,3]})
 
@method_decorator(csrf_exempt)
def UploadDAGPythonFile(request):
    if request.method == 'POST':
        S_dagFolder = os.path.join(S_dagsFolderPath, request.POST['DAG_ID'], 'UploadedFile') 
        print(type(request.POST['UploadAnyway']))
        if not os.path.exists(S_dagFolder):
            os.makedirs(S_dagFolder)
        elif request.POST['UploadAnyway'] == 'false':
            return JsonResponse({'Result':'IfUploadAnyway'})    
        
        try:
            with open(os.path.join(S_dagFolder,request.POST['DAGpyFileName']), 'w', encoding='UTF-8') as f:
                f.write(request.POST['DAGpyFileContent'])
            return JsonResponse({'Result':'success'})        
        except Exception as e:
            return JsonResponse({'Result': str(e)})        

    return JsonResponse({'AllPicDate':[1,2,3,4,5]})

def GetDAGs_buildByDAGTags_v1(request, groupName):
    L_allDAGsList = airflowConnecter.getDAGs()
    Set_tags = set([])
    for DAGChose in L_allDAGsList:
        tagsList = DAGChose.get('tags', [])
        if (DAGChose.get('dag_id', '').find(groupName) != 0):
            continue
        for tagChose in tagsList:
            if tagChose.get('name', '') == 'buildByDAGBuilder':
                for tagChose in tagsList:
                    if tagChose.get('name', '') != 'buildByDAGBuilder':
                        Set_tags.add(tagChose.get('name', ''))
                break
    D_return = {'TagList': list(Set_tags)}
    return JsonResponse(D_return)


# @method_decorator(csrf_exempt)
def GetDAGs_buildByDAGBuilder(request):
    L_allDAGsList = airflowConnecter.getDAGs()
    D_return = {'DAG_List': {}}
    
    for DAGChose in L_allDAGsList:
        tagsList = DAGChose.get('tags', [])
        for tagChose in tagsList:
            if tagChose.get('name', '') == 'buildByDAGBuilder':
                D_return['DAG_List'][DAGChose.get('dag_id')] = DAGChose
                break
    return JsonResponse(D_return)

@method_decorator(csrf_exempt)
def GetDAGRunsStatistics(request):
    if request.method == 'POST':
        L_dagRunsList = airflowConnecter.getDAGRunsList(
            request.POST['DAG_ID'],
            limit=20,
            order_by=['-start_date']
        )
        D_statistics = {}
        for D_dagRunsChose in L_dagRunsList['dag_runs']:
            S_state = D_dagRunsChose.get('state','')
            if S_state != '':
                if D_statistics.get(S_state, None) != None:
                    D_statistics[S_state] += 1
                else:
                    D_statistics[S_state] = 1
            # print(D_dagRunsChose.get('state',''))

        if len(L_dagRunsList['dag_runs']) == 0:
            D_LastRun = {'Result':'none'}
        else:
            D_LastRun = {'Result':L_dagRunsList['dag_runs'][0]}

        return JsonResponse({
            'DAG_ID':request.POST['DAG_ID'],
            'DAG_runs_statistics': D_statistics,
            'LastRun' : D_LastRun,
        })
    else:
        return JsonResponse({'AllPicDate':[1,2,3]})
        
@method_decorator(csrf_exempt)
def GetDAGRunsList(request):
    if request.method == 'POST':
        L_dagRunsList = airflowConnecter.getDAGRunsList(
            request.POST['DAG_ID'],
            limit=100,
            order_by=['-start_date']
        )
        
        return JsonResponse({
            'DAG_ID':request.POST['DAG_ID'],
            'DAG_Runs': L_dagRunsList
        })
    else:
        return JsonResponse({'AllPicDate':[1,2,3]})

@method_decorator(csrf_exempt)
def uploadTaskPyFile_v1(request, groupName, dagID):
    if request.method == 'POST':
        S_dagFolder = os.path.join(S_dagsFolderPath, groupName, dagID) 
        S_dagTaskPyFileFolder = os.path.join(S_dagFolder, 'UploadedFile') 

        if not os.path.exists(S_dagTaskPyFileFolder):
            os.makedirs(S_dagTaskPyFileFolder)
        try:
            S_filePath = os.path.join(S_dagTaskPyFileFolder,request.POST['fileName'])
            # time.sleep(1)
            with open(S_filePath, 'wb') as f:
                for chunk in request.FILES['fileUploaded'].chunks():
                    f.write(chunk)
            return JsonResponse({
                'result': 'Success',
                'message': 'Upload successfully!'
            })        
        except Exception as e:
            return JsonResponse({
                'result': 'Fail',
                'message': str(e)
            }) 

    return JsonResponse({'AllPicDate':[1,2,3, 4234]})

def GetYesterdayFailTaskList_v1(request, groupName):
    try:
        S_projectFolder = os.path.join(S_dagsFolderPath, groupName)
        D_failResult = {}
        for S_dag_id in os.listdir(S_projectFolder):
            S_settingFilePath = os.path.join(S_projectFolder, S_dag_id, '.setting', 'dagSetting.json')
            if not os.path.exists(S_settingFilePath):
                continue
            S_dagFilePath = os.path.join(S_projectFolder, S_dag_id, 'DAG_buildByWebBuilder.py')
            if not os.path.exists(S_dagFilePath):
                continue
            Obj_dagFile = dagFile.dagSettingFileManager()
            D_dagSettingFileManager = Obj_dagFile.LoadDagSettingFile(S_settingFilePath)

            S_start_date_lte = "2030-01-01T00:00:00.000000+08:00"
            S_yesterday = "{}T00:00:00.000000+08:00".format(
                (datetime.datetime.now()-datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            )
            D_failResult[S_dag_id] = {
                'DAG_ID': S_dag_id,
                'failList' : [],
                'owner': D_dagSettingFileManager.get('Owner','出了點意外'),
                'scheduleString': D_dagSettingFileManager.get('ScheduleString','出了點意外'),
            }
            print(S_dag_id ,' - ',S_yesterday, " ~ " , S_start_date_lte)
            D_result = airflowConnecter.getDAGRunsList(
                S_DAG_id=S_dag_id,
                limit=100,
                order_by=['-start_date'],
                start_date_gte=S_yesterday,
                start_date_lte=S_start_date_lte
            )
            I_count = 0
            while D_result.get('dag_runs', []) != [] and I_count <= 30:
                I_count += 1
                for runInfo in D_result['dag_runs']:
                    if runInfo.get("state", '').lower() == 'failed':
                        D_failResult[S_dag_id]['failList'].append(
                            runInfo
                        )

                S_lastDatetime = D_result['dag_runs'][-1].get('start_date', '1990-01-01T00:00:00.000000+08:00')
                re_lastDatetime = re.search(
                    "(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)T(?P<hour>\d+):(?P<minute>\d+):(?P<second>\d+)(\.(?P<mill_sec>\d+))?[+-](?P<difference_hour>\d+):(?P<difference_min>\d+)",
                    S_lastDatetime
                )
                if re_lastDatetime:
                    I_mill_sec = re_lastDatetime.group('mill_sec')
                    if I_mill_sec:
                        I_mill_sec = int(I_mill_sec)
                    else:
                        I_mill_sec = 0
                    DT_lastDatetime = datetime.datetime(
                        int(re_lastDatetime.group('year')),
                        int(re_lastDatetime.group('month')),
                        int(re_lastDatetime.group('day')),
                        int(re_lastDatetime.group('hour'))+int(re_lastDatetime.group('difference_hour')),
                        int(re_lastDatetime.group('minute'))+int(re_lastDatetime.group('difference_min')),
                        int(re_lastDatetime.group('second')),
                        I_mill_sec, 
                    ) 
                else:
                    DT_lastDatetime = datetime.datetime(1990,1,1)
                S_start_date_lte = (DT_lastDatetime-datetime.timedelta(milliseconds=1)).strftime(
                    '%Y-%m-%dT%H:%M:%S.%f'
                )
                S_start_date_lte = "{}+08:00".format(S_start_date_lte)

                D_result = airflowConnecter.getDAGRunsList(
                    S_DAG_id=S_dag_id,
                    limit=100,
                    order_by=['-start_date'],
                    start_date_gte=S_yesterday,
                    start_date_lte=S_start_date_lte
                )

            if D_failResult[S_dag_id]['failList'] == []:
                del D_failResult[S_dag_id]

        return JsonResponse({
            'result': 'Success',
            'info': D_failResult,
        })

    except Exception as e:
        return JsonResponse({
            'result': 'Fail',
            'mseeage': str(e),
        })

def GetDAGOnAirjob(request):
    pass

@method_decorator(csrf_exempt)     
def GetDAGSourseCode(request):
    try:
        # S_DAGContent = airflowConnecter.getDAGSourceCode(
        #     request.POST['fileToken'],
        # )

        # return JsonResponse({
        #     'DAG_ID':request.POST['DAG_ID'],
        #     'fileToken': request.POST['fileToken'],
        #     'result': S_DAGContent['content']
        # })
        S_dagPyFilePath = os.path.join(S_dagsFolderPath,request.POST['DAG_ID'],'DAG_buildByWebBuilder.py')
        with open(S_dagPyFilePath, 'r', encoding='utf-8') as f:
            S_DAGContent = f.read()
        return JsonResponse({
            'DAG_ID':request.POST['DAG_ID'],
            'result': S_DAGContent
        })

    except Exception as e:
        return JsonResponse({
            'mseeage': str(e)
        })

@method_decorator(csrf_exempt)     
def GetDAGSourseCode_v1(request, groupName, dagID):
    try:
        S_dagPyFilePath = os.path.join(S_dagsFolderPath ,groupName,dagID,'DAG_buildByWebBuilder.py')
        with open(S_dagPyFilePath, 'r', encoding='utf-8') as f:
            S_DAGContent = f.read()
        return JsonResponse({
            'DAG_ID': dagID,
            'result': S_DAGContent
        })

    except Exception as e:
        return JsonResponse({
            'mseeage': str(e)
        })

@method_decorator(csrf_exempt)     
def TriggerNewDagRun_v1(request, dagID):
    try:
        D_trigerResult = airflowConnecter.triggerNewDagRun(dagID)
        return JsonResponse({
            'DAG_ID': dagID,
            'result': D_trigerResult
        })

    except Exception as e:
        return JsonResponse({
            'mseeage': str(e)
        })

@method_decorator(csrf_exempt)     
def GetDAGRunLogByRunID_v1(request, dagID, runID):
    try:
        D_TaskInstances = airflowConnecter.getTaskInstances(
            dagID,
            runID
        )
        for D_taskInfo in D_TaskInstances.get("task_instances",[]):
            S_taskID = D_taskInfo['task_id']
            I_tryNumber = D_taskInfo['try_number']
            D_taskInfo['Logs'] = []
            for i in range(1,I_tryNumber+1):
                D_taskInfo['Logs'].append(airflowConnecter.getTaskInstanceLog(
                    dagID,
                    runID,
                    S_taskID,
                    i
                ))
        return JsonResponse({
            'DAG_ID': dagID,
            'Run_ID': runID,
            'result': D_TaskInstances
        })

    except Exception as e:
        return JsonResponse({
            'mseeage': str(e)
        })

def GetAllProjectList_v1(request):
    try:
        
        return JsonResponse({
            'Result': 'Success',
            'ProjectList':os.listdir(S_dagsFolderPath),
        })

    except Exception as e:
        return JsonResponse({
            'Result': 'Fail',
            'message': str(e)
        })

@method_decorator(csrf_exempt)     
def GetImportErrorList(request):
    try:
        D_ImportErrors = airflowConnecter.getImportErrors()

        return JsonResponse(D_ImportErrors)
    except Exception as e:
        return JsonResponse({
            'message': str(e)
        })
        
@method_decorator(csrf_exempt)
def GetFilesInDAGFolder_v1(request, groupName, dagID):
    try:
        S_dagFolder = os.path.join(S_dagsFolderPath, groupName, dagID, 'UploadedFile') 
        if not os.path.exists(S_dagFolder):
            os.makedirs(S_dagFolder)
        D_folderInfo = SearchFolder(S_dagFolder)
        
        return JsonResponse({
            'DAG_ID':dagID,
            'folderInfo': D_folderInfo,
        })

    except Exception as e:
        return JsonResponse({
            'message': str(e)
        })

@method_decorator(csrf_exempt)
def GetTaskInstances(request):
    try:
        if request.method == 'POST':
            # params.append("DAG_ID", D_runsInfo.dag_id)
			# params.append("DAG_RUN_ID", D_runsInfo.dag_run_id)
            D_TaskInstances = airflowConnecter.getTaskInstances(
                request.POST['DAG_ID'],
                request.POST['DAG_RUN_ID'],
            )

            return JsonResponse(D_TaskInstances)
        return JsonResponse({'AllPicDate':[1,2,3]})
    except Exception as e:
        return JsonResponse({
            'mseeage': str(e)
        })
        
@method_decorator(csrf_exempt)
def GetTaskInstanceLog(request):
    try:
        if request.method == 'POST':
            # params.append("DAG_ID", D_runsInfo.dag_id)
			# params.append("DAG_RUN_ID", D_runsInfo.dag_run_id)
            D_TaskInstanceLog = airflowConnecter.getTaskInstanceLog(
                request.POST['DAG_ID'],
                request.POST['DAG_RUN_ID'],
                request.POST['TASK_ID'],
                request.POST['LOG_INDEX'],
            )

            return JsonResponse(D_TaskInstanceLog)
        return JsonResponse({'AllPicDate':[1,2,3]})
    except Exception as e:
        return JsonResponse({
            'mseeage': str(e)
        })

def GetAllDAGIDList(request):
    Set_dagList = set([])

    L_projectName = os.listdir(S_dagsFolderPath)
    for S_projectNameChose in L_projectName:
        S_projectFolderPath = os.path.join(S_dagsFolderPath, S_projectNameChose)
        L_dagID = os.listdir(S_projectFolderPath)
        for S_dagIDChose in L_dagID:
            S_dagSettingFilePath = os.path.join(S_projectFolderPath, S_dagIDChose, '.setting', 'dagSetting.json')
            S_dagPyFilePath = os.path.join(S_projectFolderPath, S_dagIDChose, 'DAG_buildByWebBuilder.py')

            if os.path.exists(S_dagSettingFilePath):
                Set_dagList.add(S_dagIDChose)
                
            if os.path.exists(S_dagPyFilePath):
                Set_dagList.add(S_dagIDChose)


    # 此處在找出為 DAG Builder 建立的，且Import 正常的DAG List
    L_allDAGsList = airflowConnecter.getDAGs()
    for DAGChose in L_allDAGsList:
        Set_dagList.add(DAGChose.get('dag_id'))

    L_ImportErrors = airflowConnecter.getImportErrors()['import_errors']
    	# "/root/airflow/dags/Test_Fail.py"
        # /root/airflow/dags => ./airflowDagsFolder/
    for D_importErrorInfo in L_ImportErrors:
        S_dagFilePath = D_importErrorInfo.get('filename','')
        Re_dagFilePath = re.search(r'\/root\/airflow\/dags\/dagBuilder\/(?P<project>.*)\/(?P<dag_ID>.*)\/DAG_buildByWebBuilder\.py', S_dagFilePath)
        if Re_dagFilePath:
            S_dagID = Re_dagFilePath.group("dag_ID")
            Set_dagList.add(S_dagID)
        else:
            pass
        


    return JsonResponse({'dag_list': list(Set_dagList)})

@method_decorator(csrf_exempt)
def GetDAGPauseStatus(request):
    try:
        if request.method == 'POST':
            D_dagBasicInfo = airflowConnecter.getDAGBasicInfo(request.POST['DAG_ID'])
            D_dagBasicInfo['is_paused']
            
            return JsonResponse({
                'DAG_ID': request.POST['DAG_ID'],
                'is_paused' : D_dagBasicInfo['is_paused']
            })
        return JsonResponse({'AllPicDate':[1,2,3]})
    except Exception as e:
        return JsonResponse({
            'mseeage': str(e)
        })

@method_decorator(csrf_exempt)
def GetExistDAGIDList_v1(request, groupName):
    print('===============',groupName)
    D_allDAGInfo = {}
    S_projectFolderPath = os.path.join(S_dagsFolderPath, groupName)
    L_dagID = os.listdir(S_projectFolderPath)
    for S_dagIDChose in L_dagID:
        D_allDAGInfo[S_dagIDChose] = {
            'SettingFile' : False,
            'dagPyFile' : False,
            'ImportSuccess' : False,
            'ImportFailMessage' : '',
            'Owner': '',
            'Schedule' : '',
            'tags': [],
            'UpdateDate': '',
        }
        S_dagSettingFilePath = os.path.join(S_projectFolderPath, S_dagIDChose, '.setting', 'dagSetting.json')
        S_dagPyFilePath = os.path.join(S_projectFolderPath, S_dagIDChose, 'DAG_buildByWebBuilder.py')

        if os.path.exists(S_dagSettingFilePath):
            D_allDAGInfo[S_dagIDChose]['SettingFile'] = True
            Obj_dagFile = dagFile.dagSettingFileManager()
            D_dagSettingFileManager = Obj_dagFile.LoadDagSettingFile(S_dagSettingFilePath)
            D_allDAGInfo[S_dagIDChose]['Owner'] = D_dagSettingFileManager.get('Owner','')
            D_allDAGInfo[S_dagIDChose]['Schedule'] = D_dagSettingFileManager.get('ScheduleString','-')
            D_allDAGInfo[S_dagIDChose]['UpdateDate'] = D_dagSettingFileManager.get('UpdateDate','-')


        if os.path.exists(S_dagPyFilePath):
            D_allDAGInfo[S_dagIDChose]['dagPyFile'] = True


    # 此處在找出為 DAG Builder 建立的，且Import 正常的DAG List
    L_allDAGsList = airflowConnecter.getDAGs()
    for DAGChose in L_allDAGsList:
        tagsList = DAGChose.get('tags', [])
        for tagChose in tagsList:
            if tagChose.get('name', '') == 'buildByDAGBuilder':
                if D_allDAGInfo.get(DAGChose.get('dag_id'), None) != None:
                    D_allDAGInfo[DAGChose.get('dag_id')]['ImportSuccess'] = True
                    D_allDAGInfo[DAGChose.get('dag_id')]['buildByWebBuilder'] = True
                    D_allDAGInfo[DAGChose.get('dag_id')]['is_paused'] = DAGChose.get('is_paused')
                    D_allDAGInfo[DAGChose.get('dag_id')]['tags'] = DAGChose.get('tags')
                break
    L_ImportErrors = airflowConnecter.getImportErrors()['import_errors']
    	# "/root/airflow/dags/Test_Fail.py"
        # /root/airflow/dags => ./airflowDagsFolder/
    for D_importErrorInfo in L_ImportErrors:
        S_dagFilePath = D_importErrorInfo.get('filename','')
        Re_dagFilePath = re.search(
            r'\/root\/airflow\/dags\/dagBuilder\/{}\/(?P<dag_ID>.*)\/DAG_buildByWebBuilder\.py'.format(groupName), 
            S_dagFilePath
        )
        if Re_dagFilePath:
            S_dagID = Re_dagFilePath.group("dag_ID")
            D_allDAGInfo[S_dagID]['ImportFailMessage'] = D_importErrorInfo.get('stack_trace','')
        else:
            pass
        


    return JsonResponse(D_allDAGInfo)

@method_decorator(csrf_exempt)
def uploadDAGPauseStatus(request):
    try:
        if request.method == 'POST':
            data = QueryDict(request.body)
            D_dagBasicInfo = airflowConnecter.uploadDAGPauseStatus(
                request.POST['DAG_ID'],
                request.POST['is_paused'],
            )

            return JsonResponse(D_dagBasicInfo)
        return JsonResponse({'Warning': 'plz use POST method'})
    except Exception as e:
        print(e)
        return JsonResponse({
            'Warning': str(e),
            'test': request.body
        })

# 建立新DAG setting file
@method_decorator(csrf_exempt)
def uploadNewDAGSettingInfo_v1(request, groupName):
    '''
    Build New DAG id object
    '''
    try:
        if request.method == 'POST':
            D_dagSetting = {
                'DAG_ID': request.POST['DAG_ID'],
                'Owner': request.POST['Owner'],
                'Retries': request.POST['Retries'],
                'Retry_delay': request.POST['Retry_delay'],
                'CronString' : request.POST['CronString'],
                'ScheduleDateType': request.POST['ScheduleDateType'],
                'ScheduleTimeType': request.POST['ScheduleTimeType'],
                'ScheduleSettingInfo': json.loads(request.POST['ScheduleSettingInfo_String']),
                'ScheduleString' : request.POST['ScheduleString'],
                'Tags': json.loads(request.POST['Tags_JSONString']),
                'Description': request.POST['Description'],
                'TaskSettingList': json.loads(request.POST['TaskSettingList_JSONString']),
                'TaskSettingIndex': json.loads(request.POST['TaskSettingIndex_JSONString']),
                'UpdateDate': datetime.datetime.now().strftime('%Y-%m-%d'),
            }
            
            S_dagFolder = os.path.join(S_dagsFolderPath, groupName, request.POST['DAG_ID']) 
            S_dagSettingFolder = os.path.join(S_dagFolder, '.setting')
            if not os.path.exists(S_dagSettingFolder): 
                os.makedirs(S_dagSettingFolder)
            
            S_dagSettingFilePath = os.path.join(S_dagSettingFolder, 'dagSetting.json')
            
            Obj_dagFile = dagFile.dagSettingFileManager()
            Obj_dagFile.BuildNewDagSettingFile(S_dagSettingFilePath, D_dagSetting)
            
            S_dagPyFilePath = os.path.join(S_dagFolder, 'DAG_buildByWebBuilder.py')
            BuildByWebBuilderWithSettingJSON(S_dagPyFilePath, D_dagSetting)

            #################################################################################
            # 以下部分為強制刪除資料夾內沒在設定檔內設定要執行的所有檔案
            Set_fileList = set()
            for uuid in D_dagSetting.get('TaskSettingList',{}):
                Set_fileList.add(D_dagSetting['TaskSettingList'][uuid]['python_name'])
            S_uploadedFileFolder = os.path.join(S_dagFolder, 'UploadedFile') 
            if os.path.exists(S_uploadedFileFolder):
                for fileName in os.listdir(S_uploadedFileFolder):
                    S_fullPath = os.path.join(S_uploadedFileFolder, fileName)
                    if os.path.isfile(S_fullPath) and (fileName not in Set_fileList):
                        try:
                            os.remove(S_fullPath)
                        except:
                            pass
            else:
                os.makedirs(S_uploadedFileFolder)            


            #################################################################################

            # json.dumps(D_dagSetting, indent=4)
            print(D_dagSetting)
            return JsonResponse({
                'result': 'Success',
                'message': D_dagSetting
            })
        # time.sleep(2)    
        return JsonResponse({'Warning': 'plz use POST method'})
    except Exception as e:
        print(e)
        # time.sleep(2)
        return JsonResponse({
            'result': 'Fail',
            'message': str(e)
        })
   
@method_decorator(csrf_exempt)
def loadExistDAGSettingInfo_v1(request, groupName, dagID):
    try:
        S_dagFolder = os.path.join(S_dagsFolderPath, groupName, dagID) 
        S_dagSettingFolder = os.path.join(S_dagFolder, '.setting')
        
        S_dagSettingFilePath = os.path.join(S_dagSettingFolder, 'dagSetting.json')
        
        if not os.path.exists(S_dagSettingFilePath): 
            return JsonResponse({'Warning': "Can't find setting file for this DAG ID: {}".format(request.POST['DAG_ID'])})

        Obj_dagFile = dagFile.dagSettingFileManager()
        D_dagSettingFileManager = Obj_dagFile.LoadDagSettingFile(S_dagSettingFilePath)
        
        print(D_dagSettingFileManager)

        return JsonResponse(D_dagSettingFileManager)
    except Exception as e:
        print(e)
        return JsonResponse({
            'Warning': str(e)
        })

@method_decorator(csrf_exempt)
def checkIfExistsAttachFile_v1(request, groupName, dagID):
    try:
        if request.method == 'POST':

            S_dagAttachFilesFolder = os.path.join(S_dagsFolderPath, groupName, dagID, 'UploadedFile') 
            S_dagAttachFilePath = os.path.join(S_dagAttachFilesFolder, request.POST['fileName'])
            print(S_dagAttachFilePath)
            return JsonResponse({'Exists': os.path.exists(S_dagAttachFilePath)})

        return JsonResponse({'Warning': 'plz use POST method'})
    except Exception as e:
        print(e)
        return JsonResponse({
            'Warning': str(e)
        })

@method_decorator(csrf_exempt)
def checkIfExistsTaskPyFile_v1(request, groupName, dagID):
    try:
        if request.method == 'POST':
            S_dagTaskPyFileFolder = os.path.join(S_dagsFolderPath, groupName, dagID, 'UploadedFile') 
            S_dagTaskPyFilePath = os.path.join(S_dagTaskPyFileFolder, request.POST['fileName'])
            return JsonResponse({'Exists': os.path.exists(S_dagTaskPyFilePath)})

        return JsonResponse({'Warning': 'plz use POST method'})
    except Exception as e:
        print(e)
        return JsonResponse({
            'Warning': str(e)
        })

@method_decorator(csrf_exempt)
def MakeZipFile(request):
    try:
        if request.method == 'POST':
            L_return = []
            L_fileList = request.POST['FileList'].split(',')
            S_key = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
            S_fileNewFolderPath = os.path.join(S_tarFolder, S_key)
            if not os.path.exists(S_fileNewFolderPath):
                os.makedirs(S_fileNewFolderPath)
            S_zipFileName = '{}.zip'.format(S_key)
            S_zipFileFullpath = os.path.join(S_fileNewFolderPath, S_zipFileName)
            zf = zipfile.ZipFile(S_zipFileFullpath, 'w', zipfile.ZIP_DEFLATED)

            for S_filePath in L_fileList:
                if os.path.isfile(S_filePath):
                    S_filePathInZip = re.search(r"airflowDagsFolder\/dagBuilder\/.*?\/(?P<path>.*)",S_filePath).group('path')
                    zf.write(S_filePath, S_filePathInZip)
                elif os.path.isdir(S_filePath):
                    for root, dirs, files in os.walk(S_filePath):
                        for file_name in files:
                            floderFullPath = os.path.join(root, file_name)
                            print(floderFullPath)
                            S_filePathInZip = re.search(
                                r"airflowDagsFolder\/dagBuilder\/.*?\/(?P<path>.*)",
                                floderFullPath
                            ).group('path')
                            zf.write(floderFullPath, S_filePathInZip)

            return JsonResponse({'Result': 'Success', 'key': S_key})

        return JsonResponse({'Result': 'Fail','Warning': 'plz use POST method'})
    except Exception as e:
        print(e)
        return JsonResponse({
            'Result': 'Fail',
            'Warning': str(e)
        })

@method_decorator(csrf_exempt)
def DownloadZipFile(request):
    try:
        S_key = request.headers.get('key')
        S_tarFileFullpath = os.path.join(S_tarFolder, S_key, "{}.zip".format(S_key))

        file = open(S_tarFileFullpath,'rb')
        response =FileResponse(file)  
        response['Content-Type']='application/octet-stream'  
        response['Content-Disposition']='attachment;filename={}'.format(request.headers.get('FileName'))  
        return response
        
    except Exception as e:
        print(e)
        return JsonResponse({
            'Result': 'Fail',
            'Warning': str(e)
        })

@method_decorator(csrf_exempt)
def DeleteZipFile(request):
    try:
        S_key = request.headers.get('key')
        S_zipFolderpath = os.path.join(S_tarFolder, S_key)
        shutil.rmtree(S_zipFolderpath)
        return JsonResponse({
            'Result': 'Success',
            'Warning': ''
        })
    except Exception as e:
        print(e)
        return JsonResponse({
            'Result': 'Fail',
            'Warning': str(e)
        })

@method_decorator(csrf_exempt)
def DeleteUploadedFile(request):
    try:
        if request.method == 'POST':
            S_filePath = request.POST['fileFullPath']
            D_return = {
                'Result': 'Success',
                'File': '',
                'Folder': '',
            }

            if os.path.exists(S_filePath):
                if os.path.isdir(S_filePath):
                    shutil.rmtree(S_filePath)
                    D_return['Folder'] = os.path.split(S_filePath)[-1]
                elif os.path.isfile(S_filePath):
                    os.remove(S_filePath)
                    D_return['File'] = os.path.split(S_filePath)[-1]


            return JsonResponse(D_return)
        else:
            return JsonResponse({'Result': 'Fail','Warning': 'plz use POST method'})

    except Exception as e:
        print(e)
        return JsonResponse({
            'Result': 'Fail',
            'Warning': str(e)
        })

@method_decorator(csrf_exempt)
def DeleteDAG_v1(request, groupName, dagID):
    try:
        if request.method == 'DELETE':
            S_dagFolder = os.path.join(S_dagsFolderPath, groupName, dagID) 
            S_dagDeleteFolder = os.path.join(S_dagsDeletedPath, groupName) 
            if not os.path.exists(S_dagDeleteFolder):
                os.makedirs(S_dagDeleteFolder)
            print('==================================================')
            print('Try To Delete Folder: {}'.format(S_dagFolder))
            # os.system("sudo chmod -R 777 {}".format(S_dagFolder))    
            try:
                shutil.move(S_dagFolder,S_dagDeleteFolder)
            except:
                pass
            S_timeSettingPath = os.path.join(S_dagDeleteFolder, dagID, 'deleteTime.txt')
            with open(S_timeSettingPath, 'w') as f:
                f.write(datetime.datetime.now().strftime('%Y-%m-%d'))

            # shutil.rmtree(S_dagFolder, ignore_errors=True)
            shutil.rmtree(S_dagFolder, ignore_errors=True)
            # shutil.rmtree(S_dagFolder, ignore_errors=True)

            return JsonResponse({'result': 'Success'})
        return JsonResponse({'Warning': 'plz use DELETE method'})
    except Exception as e:
        print(e)
        return JsonResponse({
            'Warning': str(e)
        })
    pass

def BuildByWebBuilderWithSettingJSON(S_pyPath, D_dagSetting):
    if (D_dagSetting['ScheduleDateType'] == "One time"):
        S_startTimeStr = "datetime.strptime('{} {}','%Y-%m-%d %H:%M')".format(
            D_dagSetting['ScheduleSettingInfo']['Date'],
            D_dagSetting['ScheduleSettingInfo']['Time']
        )
    else :
        # S_startTimeStr =  'now() - timedelta(days=1)'
        S_startTimeStr =  'datetime(2000,1,1)'
    
    print(S_pyPath)
    with open(S_pyPath, 'w', encoding='utf-8') as f:
        S_pyContent = '''import os
import shutil
import pendulum
from datetime import datetime, timedelta
import airflow
from airflow.utils import timezone
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.utils.trigger_rule import TriggerRule

now = timezone.utcnow
local_tz = pendulum.timezone('Asia/Taipei')

def getBashCommandString(S_pythonName):
    S_pythonFullPath = os.path.join(os.path.split(os.path.realpath(__file__))[0],'UploadedFile',S_pythonName)
    if os.path.exists(S_pythonFullPath):
        S_bashCommand = "python3 {python_file_path}".format(python_file_path=S_pythonFullPath)
        return S_bashCommand
    raise Exception('找不到檔案: {}'.format(S_pythonName))

default_args = {
    'owner': "'''+D_dagSetting['Owner']+'''",
    'email': ['leekaiping@cathaylife.com.tw'],
    'email_on_failure': False,
    'email_on_retry': False,
    'depends_on_past': False,
    'start_date': ('''+S_startTimeStr+''').replace(tzinfo=local_tz),
    'retries': ''' +D_dagSetting['Retries'] +''',
    'retry_delay': timedelta(minutes='''+D_dagSetting['Retry_delay']+'''),
}

dag = DAG(
    dag_id="'''+D_dagSetting['DAG_ID']+'''", 
    description='''+"'''{}'''".format(D_dagSetting['Description'])+''',
    default_args=default_args,
    schedule_interval="'''+D_dagSetting['CronString']+'''",
    catchup=False,
    template_searchpath=os.path.split(os.path.realpath(__file__))[0],
    tags=['buildByDAGBuilder','''+','.join(
        ['"{}"'.format(Tag) for Tag in D_dagSetting['Tags']]
        )+'''],
)

START = DummyOperator(
    task_id='START',
    dag=dag
)

END = DummyOperator(
    task_id='END',
    dag=dag
)

'''
        L_taskList = []
        for S_taskKeyChose in D_dagSetting["TaskSettingIndex"]:
            D_taskInfo = D_dagSetting['TaskSettingList'][S_taskKeyChose]
            print(D_taskInfo)
            if D_taskInfo['type'] == 'BashOperator':
                S_taskStr = "{task_id} = BashOperator(\n    task_id='{task_id}',\n    bash_command=getBashCommandString('{python_name}'),\n    dag=dag,\n    trigger_rule=TriggerRule.ALL_DONE\n    )\n\t\n"
                S_pyContent += S_taskStr.format(task_id=D_taskInfo["tesk_id"],python_name=D_taskInfo["python_name"])
                L_taskList.append(D_taskInfo["tesk_id"])

        S_pyContent += ' >> '.join(['START'] + L_taskList + ['END'])

        f.write(S_pyContent)
