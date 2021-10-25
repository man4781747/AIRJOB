from django.conf.urls import url
from django.urls import include, path
from . import views

'''
設定 API
1. test/   測試 Django 正常與否API
2. GetOneBoardName/ 傳送單個討論版名稱給使用者
'''
urlpatterns = [
    url(r'test/', views.test),
    url(r'mainHTML/', views.mainHTML),
    path(r'testHTML/<groupName>/', views.testHTML),
    path(r'testHTML/', views.Airflow_ProjectManager_HTML),

    # ======================
    # ======= v1 API =======
    # ======================
    path(r'API/v1/GetAllProjectList/', views.GetAllProjectList_v1),

    # url(r'GetExistDAGIDList/', views.GetExistDAGIDList),
    path(r'API/v1/<groupName>/GetExistDAGIDList/', views.GetExistDAGIDList_v1),

    # url(r'uploadNewDAGSettingInfo/', views.uploadNewDAGSettingInfo),
    path(r'API/v1/<groupName>/uploadNewDAGSettingInfo/', views.uploadNewDAGSettingInfo_v1),

    # url(r'checkIfExistsTaskPyFile/', views.checkIfExistsTaskPyFile),
    path(r'API/v1/<groupName>/checkIfExistsTaskPyFile/<dagID>/', views.checkIfExistsTaskPyFile_v1),

    # url(r'UploadAttachFile/', views.UploadAttachFile),
    path(r'API/v1/<groupName>/UploadAttachFile/<dagID>/', views.UploadAttachFile_v1),

    # url(r'GetDAGSourseCode/', views.GetDAGSourseCode),
    path(r'API/v1/<groupName>/GetDAGSourseCode/<dagID>/', views.GetDAGSourseCode_v1),

    # url(r'GetFilesInDAGFolder/', views.GetFilesInDAGFolder),
    path(r'API/v1/<groupName>/GetFilesInDAGFolder/<dagID>/', views.GetFilesInDAGFolder_v1),

    # url(r'loadExistDAGSettingInfo/', views.loadExistDAGSettingInfo),
    path(r'API/v1/<groupName>/loadExistDAGSettingInfo/<dagID>/', views.loadExistDAGSettingInfo_v1),

    # url(r'uploadTaskPyFile/', views.uploadTaskPyFile),
    path(r'API/v1/<groupName>/uploadTaskPyFile/<dagID>/', views.uploadTaskPyFile_v1),

    # url(r'checkIfExistsAttachFile/', views.checkIfExistsAttachFile),
    path(r'API/v1/<groupName>/checkIfExistsAttachFile/<dagID>/', views.checkIfExistsAttachFile_v1),

    path(r'API/v1/GetDAGRunLogByRunID/<dagID>/<runID>/', views.GetDAGRunLogByRunID_v1),

    path(r'API/v1/TriggerNewDagRun/<dagID>/', views.TriggerNewDagRun_v1),

    path(r'API/v1/<groupName>/DeleteDAG/<dagID>/', views.DeleteDAG_v1),

    # url(r'GetDAGs_buildByDAGTags/', views.GetDAGs_buildByDAGTags),
    path(r'API/v1/<groupName>/GetDAGs_buildByDAGTags/', views.GetDAGs_buildByDAGTags_v1),

    path(r'API/v1/<groupName>/GetYesterdayFailTaskList_v1/', views.GetYesterdayFailTaskList_v1),


    # ======================
    # ======= v0 API =======
    # ======================

    url(r'GetImportErrorList/', views.GetImportErrorList),
    url(r'GetDAGRunsStatistics/', views.GetDAGRunsStatistics),
    url(r'GetAllDAGIDList/', views.GetAllDAGIDList),
    url(r'GetDAGPauseStatus/', views.GetDAGPauseStatus),
    url(r'uploadDAGPauseStatus/', views.uploadDAGPauseStatus),
    url(r'MakeZipFile/', views.MakeZipFile),
    url(r'DownloadZipFile/', views.DownloadZipFile),
    url(r'DeleteZipFile/', views.DeleteZipFile),
    url(r'DeleteUploadedFile/', views.DeleteUploadedFile),
    url(r'UploadDAGPythonFile/', views.UploadDAGPythonFile),
    url(r'GetDAGs/', views.GetDAGs_buildByDAGBuilder),
    url(r'GetDAGRunsList/', views.GetDAGRunsList),
    url(r'GetTaskInstances/', views.GetTaskInstances),
    url(r'GetTaskInstanceLog/', views.GetTaskInstanceLog),
    
]
