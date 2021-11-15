import json
import requests
import datetime
import uuid
import traceback
from websocket import create_connection
import re
from airflow.exceptions import AirflowFailException
import sys
import os
sys.path.append(os.path.split(os.path.realpath(__file__))[0])
import tokenTransform
import urllib.parse
import time

S_airjobUrl = "http://88.248.13.72:8900/AirFlowUploadWeb/testHTML/{}/?Page=dagInfoView&dag_id={}&SheetChose=DAG_Infomation"

def send_execute_request(code):
    msg_type = 'execute_request';
    content = { 'code' : code, 'silent':False }
    hdr = { 'msg_id' : uuid.uuid1().hex, 
        'username': 'test', 
        'session': uuid.uuid1().hex, 
        'data': datetime.datetime.now().isoformat(),
        'msg_type': msg_type,
        'version' : '5.0' }
    msg = { 'header': hdr, 'parent_header': hdr, 
        'metadata': {},
        'content': content }
    return msg

def run(S_jupyterNotebookUrl='', S_jupyterToken='', S_dagID=''):
    if S_jupyterNotebookUrl == '':
        raise AirflowFailException("無jupyterNotebookUrl")
    if S_jupyterToken == '':
        raise AirflowFailException("無jupyter Token")
    if S_dagID == '':
        raise AirflowFailException("無 dagID")

    try:
        S_jupyterToken = tokenTransform.dectry(S_jupyterToken)
    except:
        pass

    S_jupyterNotebookUrl = urllib.parse.unquote(S_jupyterNotebookUrl)

    Re_jupyterNotebookUrl = re.search(r"^(?P<jupyter_url>.*)/notebooks/(?P<notebook_path>.*)", S_jupyterNotebookUrl)
    if not Re_jupyterNotebookUrl:
        print('URL Format 錯誤')
        print(S_jupyterNotebookUrl)
        raise AirflowFailException("URL 格式錯誤，找不到檔案")
    print('嘗試執行Jupyter檔案: {}'.format(S_jupyterNotebookUrl))

    try:
        notebook_path = '/' + Re_jupyterNotebookUrl.group('notebook_path').split('?')[0].split('#')[0]
        base = Re_jupyterNotebookUrl.group('jupyter_url')
        headers = {'Authorization': S_jupyterToken}
        S_ip_port = base.split('//')[-1]
        print('建立新kernel')
        S_URL_NewKernels = base + '/api/kernels'+ "?token={}".format(S_jupyterToken)
        response = requests.post(S_URL_NewKernels)
        D_return = json.loads(response.text)
        D_kernel = D_return
        print("建立新kernel成功: {}".format(D_kernel['id']))
    except Exception as e:
        print(e)
        raise AirflowFailException("建立新kernel失敗，請聯絡工程組")

    # try:
    #     notebook_path = '/' + Re_jupyterNotebookUrl.group('notebook_path').split('?')[0].split('#')[0]
    #     base = Re_jupyterNotebookUrl.group('jupyter_url')
    #     headers = {'Authorization': S_jupyterToken}
    #     S_ip_port = base.split('//')[-1]
        
    #     url = base + '/api/sessions' + "?token={}".format(S_jupyterToken)

    #     params = '{"path":\"%s\","type":"notebook","name":"","kernel":{"id":null,"name":"python3"}}' % notebook_path
    #     response = requests.post(url, headers=headers, data=params.encode('utf-8'))
    #     session = json.loads(response.text)
    #     kernel = session["kernel"]
    # except Exception as e:
    #     print(e)
    #     raise AirflowFailException("登入Jupyter失敗，請確認Token以及URL提供正確")
    
    try:
        print("讀取notebook檔案，並獲取每個Cell裡的Code")
        url = base + '/api/contents' + notebook_path + "?token={}".format(S_jupyterToken)
        response = requests.get(url,headers=headers)
        file = json.loads(response.text)
        code = [ [c['source'],index] for index,c in enumerate(file['content']['cells']) if c['cell_type']=='code' if len(c['source'])>0 ]   
    except Exception as e:
        print(e)
        raise AirflowFailException("獲得NoteBook內容失敗，請確認Token以及URL提供正確")

    try:
        print("開始啟動 WebSocket channels")
        S_ws_url = "ws://{}/api/kernels/".format(S_ip_port)+D_kernel["id"]+"/channels?"+"token={}".format(S_jupyterToken)
        ws = create_connection(
            S_ws_url, 
            header=headers)
        B_hasFail = False    

        for L_c in code:
            print(
                '\n執行第{}區塊的code:\n================= START =================\n{}\n=================  END  ================='.format(L_c[1]+1,L_c[0])
            )
            ws.send(json.dumps(send_execute_request(L_c[0])))
            try:
                msg_type = ''
                S_resultString = "\n執行結果:"
                while True:
                    time.sleep(0.1)
                    rsp = json.loads(ws.recv())
                    msg_type = rsp["msg_type"]
                    if msg_type == "stream":
                        S_resultString += "\n{}".format(rsp["content"]["text"])
                        file['content']['cells'][L_c[1]]['outputs'] = [
                            {
                            'name': rsp["content"]["name"], 
                            'output_type': 'stream', 
                            'text': rsp["content"]["text"]
                            },
                            {
                            'name': 'stdout', 
                            'output_type': 'stream', 
                            'text': "\n===== 以上由AIRJOB觸發並更新 =====\n===== 觸發時間: {}\n===== AIRJOB 網址:{}\n".format(
                                datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f"),
                                S_airjobUrl.format(S_dagID.split('_')[0],S_dagID)
                                )
                            },
                        ]
                    elif msg_type == "execute_result":
                        if "image/png" in (rsp["content"]["data"].keys()):
                            S_resultString += "\n{}".format(rsp["content"]["data"]["image/png"])
                        else:
                            S_resultString += "\n{}".format(rsp["content"]["data"]["text/plain"])
                    elif msg_type == "display_data":
                        S_resultString += "\n{}".format(rsp["content"]["data"]["image/png"])
                        file['content']['cells'][L_c[1]]['outputs'] = [
                            {
                            "output_type": "display_data",
                            "data" : rsp["content"]['data'],
                            "metadata": rsp["content"]['metadata']
                            },
                            {
                            'name': 'stdout', 
                            'output_type': 'stream', 
                            'text': "\n===== 以上由AIRJOB觸發並更新 =====\n===== 觸發時間: {}\n===== AIRJOB 網址:{}\n".format(
                                datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f"),
                                S_airjobUrl.format(S_dagID.split('_')[0],S_dagID)
                                )
                            },
                        ]
                    elif msg_type == "error":
                        S_resultString += "\n{}".format(rsp["content"]["traceback"])
                        B_hasFail = True
                        file['content']['cells'][L_c[1]]['outputs'] = [                        
                            {
                            "output_type": "error",
                            "ename" : rsp["content"]['ename'],
                            "evalue": rsp["content"]['evalue'],
                            "traceback": rsp["content"]['traceback'],
                            },
                            {
                            'name': 'stdout', 
                            'output_type': 'stream', 
                            'text': "\n===== 以上由AIRJOB觸發並更新 =====\n===== 觸發時間: {}\n===== AIRJOB 網址:{}\n".format(
                                datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f"),
                                S_airjobUrl.format(S_dagID.split('_')[0],S_dagID)
                                )
                            },
                        ]

                    elif msg_type == "execute_reply" and rsp["content"]["status"] == "aborted":
                        S_resultString += "\n跳過"
                        file['content']['cells'][L_c[1]]['outputs'] = [                        
                            {
                            'name': "stdout", 
                            'output_type': 'stream', 
                            'text': "因前方有錯誤，跳過"
                            },
                            {
                            'name': 'stdout', 
                            'output_type': 'stream', 
                            'text': "\n===== 以上由AIRJOB觸發並更新 =====\n===== 觸發時間: {}\n===== AIRJOB 網址:{}\n".format(
                                datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f"),
                                S_airjobUrl.format(S_dagID.split('_')[0],S_dagID)
                                )
                            },
                        ]

                    elif msg_type == "status" and rsp["content"]["execution_state"] == "idle":
                        print(S_resultString)
                        break
                        
            except:
                traceback.print_exc()
    except Exception as e:
        try:
            ws.close()
        except:
            pass
        raise AirflowFailException("與Jupyter WebSocket連線失敗，請確認Token以及URL提供正確")
    print('所有Code已執行完畢')
    time.sleep(0.1)            
    ws.close()
    time.sleep(0.1)
    print('刪除kernel: {}'.format(D_kernel['id']))
    S_URL_DelKernels = base + '/api/kernels/{}?token={}'.format(D_kernel['id'],S_jupyterToken)
    response = requests.delete(url,headers=headers)
    print(response.text)

    new = {
        'type': "notebook",
        'content':file['content'],
    }

    url = base + '/api/contents' + notebook_path + "?token={}".format(S_jupyterToken)
    headers["Content-Type"] =  "application/json"
    response = requests.put(url,headers=headers,data=json.dumps(new))

    if B_hasFail:
        raise AirflowFailException("Task Fail!")
    return B_hasFail

    
if __name__=='__main__':
    run("http://35.194.167.48:8001/notebooks/TestFloder/TestPyFile.ipynb","password")