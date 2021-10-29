import requests
import re
import json
import datetime

class airflowConnecter:
    def __init__(self,S_account, S_password, S_airflowURL="http://127.0.0.1:8080"):
        self.S_account = S_account
        self.S_password = S_password
        self.airflowURL = S_airflowURL
        self.S_datetimeReCheck = r"^(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)T(?P<hour>\d+):(?P<minute>\d+):(?P<second>\d+)(?P<mill_sec>\.\d+)?[+-](?P<difference_hour>\d+):(?P<difference_min>\d+)$"
        
    def getDAGs(self):
        # https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#tag/DAG
        S_getDAGs_API = '{airflowURL}/api/v1/dags'.format(airflowURL=self.airflowURL)
        try:
            D_dags = requests.get(S_getDAGs_API, auth=(self.S_account, self.S_password)).json().get('dags')
            return D_dags
        except Exception as e:
            return {'status': 'Fail', 'message': str(e)}

    def getDAGBasicInfo(self, S_DAG_id):
        # https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#operation/get_dag
        S_getDAGBasicInfo = "{airflowURL}/api/v1/dags/{dag_id}".format(airflowURL=self.airflowURL,dag_id=S_DAG_id)
        try:
            D_dagBasicInfo = requests.get(S_getDAGBasicInfo, auth=(self.S_account, self.S_password)).json()
            return D_dagBasicInfo
        except Exception as e:
            return {'status': 'Fail', 'message': str(e)}

    def getDAGTasksInfo(self, S_DAG_id):
        # https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#operation/get_tasks
        S_getDAGTasks = "{airflowURL}/api/v1/dags/{dag_id}/tasks".format(airflowURL=self.airflowURL,dag_id=S_DAG_id)
        try:
            D_dagTasks = requests.get(S_getDAGTasks, auth=(self.S_account, self.S_password)).json()
            return D_dagTasks
        except Exception as e:
            return {'status': 'Fail', 'message': str(e)}

    def getDAGSourceCode(self, S_fileToken, encoding='utf-8'):
        # https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#operation/get_dag_source
        S_getDAGSourceCode = "{airflowURL}/api/v1/dagSources/{file_token}".format(airflowURL=self.airflowURL,file_token=S_fileToken)
        # print(S_getDAGSourceCode)
        try:
            R_dagSourceCode = requests.get(S_getDAGSourceCode, auth=(self.S_account, self.S_password))
            R_dagSourceCode.encoding = encoding
            return {'content': R_dagSourceCode.text}
        except Exception as e:
            return {'content': str(e)}
    
    def getDAGRunsList(self, S_DAG_id, limit=100, offset=0, execution_date_gte='',execution_date_lte='',
    start_date_gte='',start_date_lte='',end_date_gte='',end_date_lte='',order_by=[]):
        # https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#tag/DAGRun
        #
        # datetime format example: 2021-09-02T06:00:00+08:00
        # re: \w{4}-\w{2}-\w{2}T\w{2}:\w{2}:\w{2}[+-]\w{2}:\w{2}
        #
        # https://airflow.apache.org/api/v1/dags/{dag_id}/dagRuns
        L_paras = []
        L_paras.append('limit={}'.format(limit))
        L_paras.append('offset={}'.format(offset))
        if re.search(self.S_datetimeReCheck, execution_date_gte):
            L_paras.append('execution_date_gte={}'.format(execution_date_gte))
            
        if re.search(self.S_datetimeReCheck, execution_date_lte):
            L_paras.append('execution_date_lte={}'.format(execution_date_lte))
            
        if re.search(self.S_datetimeReCheck, start_date_gte):
            L_paras.append('start_date_gte={}'.format(start_date_gte))
            
        if re.search(self.S_datetimeReCheck, start_date_lte):
            L_paras.append('start_date_lte={}'.format(start_date_lte))
            
        if re.search(self.S_datetimeReCheck, end_date_gte):
            L_paras.append('end_date_gte={}'.format(end_date_gte))
        
        if re.search(self.S_datetimeReCheck, end_date_lte):
            L_paras.append('end_date_lte={}'.format(end_date_lte))
        
        for S_orderByStr in order_by:
            L_paras.append('order_by={}'.format(S_orderByStr))
            
        S_parasString = '&'.join(L_paras)
        
        S_getDAGRunsList = "{airflowURL}/api/v1/dags/{dag_id}/dagRuns?{paras}".format(
            airflowURL=self.airflowURL,dag_id=S_DAG_id,paras=S_parasString
        )
        # print(S_getDAGRunsList)
        try:
            D_dagRunsList = requests.get(S_getDAGRunsList, auth=(self.S_account, self.S_password)).json()
            return D_dagRunsList
        except Exception as e:
            return {'status': 'Fail', 'message': str(e)}
        
    def getDAGRunInfo(self, S_DAG_id, S_DAG_run_id):
        # https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#operation/get_dag_run
        
        S_getDAGRunIngo = "{airflowURL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}".format(
            airflowURL=self.airflowURL,dag_id=S_DAG_id,dag_run_id=S_DAG_run_id
        )
        try:
            D_dagRunInfo = requests.get(S_getDAGRunIngo, auth=(self.S_account, self.S_password)).json()
            return D_dagRunInfo
        except Exception as e:
            return {'status': 'Fail', 'message': str(e)}
    
    def getImportErrors(self):
        # https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#operation/get_import_errors
        
        S_getImportErrors = "{airflowURL}/api/v1/importErrors".format(airflowURL=self.airflowURL)
        try:
            D_importErrors = requests.get(S_getImportErrors, auth=(self.S_account, self.S_password)).json()
            return D_importErrors
        except Exception as e:
            return {'status': 'Fail', 'message': str(e)}
        
    def getTaskInstances(self, S_DAG_id, S_DAG_run_id):
        # https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#operation/get_task_instances
        S_getTaskInstances = "{airflowURL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances".format(
            airflowURL=self.airflowURL,dag_id=S_DAG_id,dag_run_id=S_DAG_run_id
        )
        try:
            D_getTaskInstances = requests.get(S_getTaskInstances, auth=(self.S_account, self.S_password)).json()
            return D_getTaskInstances
        except Exception as e:
            return {'status': 'Fail', 'message': str(e)}
        
    def getTaskInstanceInfo(self, S_DAG_id, S_DAG_run_id,S_task_id):
        # https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#operation/get_task_instance
        S_getTaskInstanceInfo = "{airflowURL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}".format(
            airflowURL=self.airflowURL,dag_id=S_DAG_id,dag_run_id=S_DAG_run_id,task_id=S_task_id
        )
        try:
            D_getTaskInstanceInfo = requests.get(S_getTaskInstanceInfo, auth=(self.S_account, self.S_password)).json()
            return D_getTaskInstanceInfo
        except Exception as e:
            return {'status': 'Fail', 'message': str(e)}
        
            
    def getTaskInstanceLog(self, S_DAG_id, S_DAG_run_id,S_task_id, I_logIndex, encoding='utf-8'):
        # https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#operation/get_task_instance
        S_getTaskInstanceLog = "{airflowURL}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}/logs/{index}".format(
            airflowURL=self.airflowURL,dag_id=S_DAG_id,dag_run_id=S_DAG_run_id,task_id=S_task_id,index=I_logIndex
        )
        try:
            R_getTaskInstanceLog = requests.get(S_getTaskInstanceLog, auth=(self.S_account, self.S_password))
            R_getTaskInstanceLog.encoding = encoding
            return {'content': R_getTaskInstanceLog.text}
        except Exception as e:
            return {'status': 'Fail', 'message': str(e)}

    def uploadDAGPauseStatus(self, S_DAG_id, B_is_paused):
        # https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#operation/patch_dag
        S_uploadDAGPauseStatus = "{airflowURL}/api/v1/dags/{dag_id}".format(airflowURL=self.airflowURL,dag_id=S_DAG_id)
        if B_is_paused == 'true':
            B_is_paused = True
        else:
            B_is_paused = False
        
        D_PatchData = {"is_paused": B_is_paused}
        try:
            D_getTaskInstanceLog = requests.patch(
                S_uploadDAGPauseStatus, 
                data=json.dumps(D_PatchData), 
                auth=(self.S_account, self.S_password),
                headers = {'content-type': 'application/json'}
            ).json()
            return D_getTaskInstanceLog
        except Exception as e:
            return {'status': 'Fail', 'message': str(e)}

    def triggerNewDagRun(self, S_DAG_id):
        # https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html#operation/post_dag_run
        try:
            S_triggerNewDagRun = "{airflowURL}/api/v1/dags/{dag_id}/dagRuns".format(airflowURL=self.airflowURL,dag_id=S_DAG_id)
            S_datetime = (datetime.datetime.now() + datetime.timedelta(seconds=3)).astimezone().isoformat()
            D_postData = {
                "dag_run_id": 'TrigerByDjango_{}'.format(S_datetime),
                "execution_date": S_datetime,
                # "state": "queued",
                # "conf": {},
            }
            D_getTaskInstanceLog = requests.post(
                S_triggerNewDagRun, 
                auth=(self.S_account, self.S_password),
                data=json.dumps(D_postData),
                headers = {'content-type': 'application/json'}
                ).json()
            
            if D_getTaskInstanceLog.get('status',""):
                return {'status': 'Fail', 'Result': D_getTaskInstanceLog,}

            return {
                'status': 'Success',
                'Result': D_getTaskInstanceLog,
            }


        except Exception as e:
            return {'status': 'Fail', 'message': str(e)}


if __name__ == '__main__':    
    S_airflowURL = 'http://34.80.102.147:8080'
    S_account = 'TestAccount@gmail.com'
    S_password = 'password'
    Obj_airflowConnecter = airflowConnecter(S_account, S_password,S_airflowURL)


    # D_dags = Obj_airflowConnecter.getDAGs()[0]
    # print(D_dags)

    # D_dagBasicInfo = Obj_airflowConnecter.getDAGBasicInfo(D_dags.get('dag_id'))
    # print(D_dagBasicInfo)

    # D_dagTasksInfo = Obj_airflowConnecter.getDAGTasksInfo(D_dags.get('dag_id'))
    # print(D_dagTasksInfo)

    # D_dagSourceCode = Obj_airflowConnecter.getDAGSourceCode(D_dags.get('file_token'))
    # print(D_dagSourceCode)

    # D_dagRunsList = Obj_airflowConnecter.getDAGRunsList(
        # D_dags.get('dag_id'),
        # limit=10, offset=0,order_by=['-start_date']
    # )
    # print(D_dagRunsList.get('dag_runs'))

    # D_DAGRunInfo = Obj_airflowConnecter.getDAGRunInfo(
        # D_dags.get('dag_id'),
        # D_dagRunsList.get('dag_runs')[0].get('dag_run_id')
    # )
    # print(D_DAGRunInfo)

    # D_TaskInstances = Obj_airflowConnecter.getTaskInstances(
            # D_dags.get('dag_id'),
            # D_dagRunsList.get('dag_runs')[0].get('dag_run_id')
    # )
    # print(D_TaskInstances)

    # D_TaskInstanceInfo = Obj_airflowConnecter.getTaskInstanceInfo(
            # D_dags.get('dag_id'),
            # D_dagRunsList.get('dag_runs')[0].get('dag_run_id'),
            # 'BashOperator_Default_1'
    # )
    # print(D_TaskInstanceInfo)
    
    # S_TaskInstanceLog = Obj_airflowConnecter.getTaskInstanceLog(
            # D_dags.get('dag_id'),
            # D_dagRunsList.get('dag_runs')[0].get('dag_run_id'),
            # 'BashOperator_Default_1',
            # 1
    # )
    # print(S_TaskInstanceLog)
    
    
    D_TaskInstanceLog = Obj_airflowConnecter.uploadDAGPauseStatus(
        'Test123456', True
    )
    
    print(D_TaskInstanceLog)