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

S_airjobUrl = "http://35.194.167.48:8893/AIRJOB/{}/?Page=dagInfoView&dag_id={}&SheetChose=DAG_Infomation"

D_AIRJOB_Jupyter_metadata = {
    '9h000': {
        'url':'http://35.194.167.48:5567',
        'token':'password',
    },
    '9h001': {
        'url':'http://35.194.167.48:5567',
        'token':'password',
    },
    '9h002': {
        'url':'http://35.194.167.48:5567',
        'token':'password',
    },
}

def send_execute_request(code):
    msg_type = 'execute_request'
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

def airjobOutputInfo(S_dagID):
    L_returnList = [
    "<style>\n",
    ".airjob-infos-window {\n",
    "    margin-top: .5rem;border-radius: 10px;box-shadow: 2px 2px 2px 1px rgb(23 162 184 / 0%);transition:all .5s;cursor: pointer;\n",
    "}\n",
    ".airjob-infos-window:hover {\n",
    "    box-shadow: 2px 2px 2px 1px rgb(23 162 184 / 40%);\n",
    "}\n",
    ".airjob-infos-bar {\n",
    "    background-color:#17a2b8;height:10px;border-top-right-radius: 10px;border-top-left-radius: 10px;\n",
    "}\n",
    ".airjob-infos-contents {\n",
    "    border: 1px #17a2b8 solid;padding: 0.8rem 0.5rem;border-bottom-right-radius: 10px;border-bottom-left-radius: 10px;\n",
    "}\n",
    ".airjob-infos-title {\n",
    "    font-weight:600;font-size:2rem;\n",
    "}\n",
    "</style>\n",
    "<div class=\"airjob-infos-window\">\n",
    "    <div class=\"airjob-infos-bar\"></div>\n",
    "    <div class=\"airjob-infos-contents\">\n",
    "        <div class=\"airjob-infos-title\">以上由AIRJOB觸發並更新</div>\n",
    "        <div>觸發時間: {}</div>\n".format(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")),
    "        <a href='{url}' target=_blank>AIRJOB 網址:{url}</a>\n".format(url = S_airjobUrl.format(S_dagID.split('_')[0],S_dagID)),
    "    </div>\n",
    "</div>",
    ]
    return L_returnList

def DeleteKernel(S_kernelID, S_JuypterToken, S_JupyterURL):
    print('準備刪除kernel: {}'.format(S_kernelID))
    S_URL_DelKernels = S_JupyterURL + '/api/kernels/{}?token={}'.format(S_kernelID,S_JuypterToken)
    for try_num in range(5):
        response = requests.delete(S_URL_DelKernels)
        print(response.status_code)
        if response.status_code < 300:
            print('刪除kernel成功: {}'.format(S_kernelID))
            break
        print('刪除kernel失敗，準備重試: {}'.format(try_num))
    else:
        print('刪除kernel: {} 失敗!!'.format(S_kernelID))

def run(S_jupyterNotebookUrl='', S_jupyterToken='', S_dagID=''):
    if S_jupyterNotebookUrl == '':
        raise AirflowFailException("無jupyterNotebookUrl")
    if S_jupyterToken == '':
        raise AirflowFailException("無jupyter Token")
    if S_dagID == '':
        raise AirflowFailException("無 dagID")

    S_project = S_dagID.split('_')[0]
    if D_AIRJOB_Jupyter_metadata.get(S_project, None) == None:
        raise AirflowFailException("找不到project: {} 的設定資料，請通知工程組處理。".format(S_project))

    try:
        S_jupyterToken = tokenTransform.dectry(S_jupyterToken)
    except:
        pass

    S_jupyterNotebookUrl = urllib.parse.unquote(S_jupyterNotebookUrl)

    L_reList = [
        r"^(?P<jupyter_url>.*)/notebooks/(?P<notebook_path>.*)",
        r"^(?P<jupyter_url>.*)/edit/(?P<notebook_path>.*)",
        r"^(?P<jupyter_url>.*)/lab.*/tree/(?P<notebook_path>.*)",
    ]

    for S_reStr in L_reList:
        Re_jupyterNotebookUrl = re.search(S_reStr, S_jupyterNotebookUrl)
        if Re_jupyterNotebookUrl:
            break
    else:
        print('URL Format 錯誤')
        print(S_jupyterNotebookUrl)
        raise AirflowFailException("URL 格式錯誤，找不到檔案")

    print('嘗試執行Jupyter檔案: {}'.format(S_jupyterNotebookUrl))

    notebook_path = '/' + Re_jupyterNotebookUrl.group('notebook_path').split('?')[0].split('#')[0]
    S_userJupyterUrl = Re_jupyterNotebookUrl.group('jupyter_url')

    #先在Jupyter內獲得檔案內容
    try:
        print("讀取notebook檔案，並獲取每個Cell裡的Code")
        url = S_userJupyterUrl + '/api/contents' + notebook_path + "?token={}".format(S_jupyterToken)
        response = requests.get(url)
        file = json.loads(response.text)
        if file['type'] == "notebook":
            S_fileType = 'notebook'
            print('偵測為Notebook檔案')
            code = [ [c['source'],index] for index,c in enumerate(file['content']['cells']) if c['cell_type']=='code' if len(c['source'])>0 ]   
        elif file['type'] == "file" and file['mimetype'] == "text/x-python":
            S_fileType = 'pyfile'
            print('偵測為.py檔案')
            code = file['content']
        else:
            raise AirflowFailException("未知格式檔案")
    except Exception as e:
        print(e)
        raise AirflowFailException("獲得NoteBook內容失敗，請確認Token以及URL提供正確")

    #尋找name為uuid_開頭並Kernels狀態為idle而且last_activity大於5分鐘前的session，並關閉他們(主要是盡量清空之前關失敗的kernel)
    try:
        print('準備掃描AIRJOB專用Jupyter閒置的Kernels')
        D_AIRJOB_JupyterInfo = D_AIRJOB_Jupyter_metadata[S_project]
        S_sessions_url = D_AIRJOB_JupyterInfo['url'] + "/api/sessions?token={}".format(D_AIRJOB_JupyterInfo['token'])
        response_Kernels = requests.get(S_sessions_url)
        L_Sessions = json.loads(response_Kernels.text)
        for D_sessionInfo in L_Sessions:
            if D_sessionInfo.get('name',"xxxxxxxx")[:5] != 'uuid_':
                # 排除不是uuid_開頭的session
                continue
            try:
                DT_last_activity = datetime.datetime.strptime(D_sessionInfo.get('last_activity',''),"%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(hours=8)
                if DT_last_activity > (datetime.datetime.now() - datetime.timedelta(minutes=5)):
                    # 排除last_activity大於5分鐘前的kernel
                    continue
            except Exception as e:
                print('無法判別 last_activity: {}'.format(e))
            if D_sessionInfo.get('kernel',{}).get('execution_state','no') not in ['idle', 'starting']:
                # 排除execution_state不是idle的kernel
                continue

            print('找到沒關乾淨的kernel')
            if D_sessionInfo['kernel']['execution_state'] == 'starting':
                print('發現啟動超過5分鐘還沒啟動完畢的kernel')
            S_kernel_id = D_sessionInfo['kernel']['id']
            DeleteKernel(S_kernel_id, D_AIRJOB_JupyterInfo['token'], D_AIRJOB_JupyterInfo['url'])
        print('掃描閒置的Kernels完畢!')
    except Exception as e:
        print('掃描閒置的Kernels失敗! {}'.format(e))

    #準備與AIRJOB專用Jupyter連線
    try:
        print('準備與AIRJOB專用Jupyter連線')
        D_AIRJOB_JupyterInfo = D_AIRJOB_Jupyter_metadata[S_project]
        S_AIRJOB_JupyterRrl = D_AIRJOB_JupyterInfo['url'] + "/api/sessions?token={}".format(D_AIRJOB_JupyterInfo['token'])
        S_AIRJOBJupyter_ip_port = D_AIRJOB_JupyterInfo['url'].split('//')[-1]
        D_params = {
            "path": notebook_path+"___{}".format(uuid.uuid1().hex),
            "type":"notebook",
            "name":"uuid_{}".format(uuid.uuid1().hex),
            "kernel":{
                "id":None,
                "name":"python3"
            },
        }
        params = json.dumps(D_params)
        print('獲得session資訊')
        response = requests.post(S_AIRJOB_JupyterRrl, data=params.encode('utf-8'))
        session = json.loads(response.text)
        D_kernel = session["kernel"]
        S_sessionsUuid = session['id']
        print('建立新session成功: {}'.format(S_sessionsUuid))
        print("獲得kernel成功: {}".format(D_kernel['id']))
    except Exception as e:
        print(e)
        raise AirflowFailException("獲得kernel失敗，請聯絡工程組")



    if S_fileType=='notebook':
        try:
            print("開始啟動 WebSocket channels")
            S_ws_url = "ws://{}/api/kernels/".format(S_AIRJOBJupyter_ip_port)+D_kernel["id"]+"/channels?"+"token={}".format(D_AIRJOB_JupyterInfo['token'])
            ws = create_connection(
                S_ws_url)
            print('檢查kernel是否準備完畢')
            S_URL_CheckKernels = D_AIRJOB_JupyterInfo['url'] + '/api/kernels/{}?token={}'.format(D_kernel["id"],D_AIRJOB_JupyterInfo['token'])
            for i in range(60):
                response_checkKernels = requests.get(S_URL_CheckKernels)
                D_checkKernels = json.loads(response_checkKernels.text)
                if D_checkKernels.get('execution_state', 'starting') != 'starting':
                    print('確認kernel啟動完畢')
                    break
                time.sleep(1)
            else:
                ws.close()
                print(D_checkKernels)
                DeleteKernel(D_kernel['id'], D_AIRJOB_JupyterInfo['token'], D_AIRJOB_JupyterInfo['url'])
                raise AirflowFailException("Jupyter Kernel無法啟動成功")
        except Exception as e:
            print('=== 錯誤訊息 ===')
            print(e)
            print('===============')
            try:
                ws.close()
                # print(D_checkKernels)
            except:
                pass
            raise AirflowFailException("與Jupyter WebSocket連線失敗，請確認Token以及URL提供正確")

        B_hasFail = False   
        try:
            L_resultList = []
            # 嘗試處裡Jupyter API的錯位BUG
            print('嘗試與Jupyter溝通並檢查類型')
            msg_type = ''

            ws.send(json.dumps(send_execute_request('print("WebSocket Check")')))
            I_Try = 0
            while True and I_Try<20:
                rsp = json.loads(ws.recv())
                msg_type = rsp["msg_type"]
                if msg_type == "stream" and "WebSocket Check" in rsp["content"]["text"]:
                    break
                I_Try += 1
            else:
                ws.close()
                raise AirflowFailException("與Jupyter WebSocket溝通失敗，請通知工程組排除問題")
            I_Try = 0 
            while True and I_Try<20:
                rsp = json.loads(ws.recv())
                msg_type = rsp["msg_type"]
                if msg_type == "status" and rsp["content"]["execution_state"] == "idle":
                    break
                I_Try += 1
            else:
                ws.close()
                raise AirflowFailException("與Jupyter WebSocket溝通失敗，請通知工程組排除問題")

            print('Jupyter溝通成功')
            print('開始執行程式')
            for I_inedx,L_c in enumerate(code):
                print(
                    '\n執行第{}區塊的code:\n================= START =================\n{}\n=================  END  ================='.format(
                    L_c[1]+1,
                    L_c[0])
                )

                ws.send(json.dumps(send_execute_request(L_c[0])))
                try:
                    msg_type = ''
                    S_resultString = "\n執行結果:"
                    file['content']['cells'][L_c[1]]['outputs'] = []
                    while True:
                        rsp = json.loads(ws.recv())
                        msg_type = rsp["msg_type"]
                        # print('***********************************************************************')
                        # print(rsp)
                        # print('***********************************************************************')
                        if msg_type == "stream":
                            S_resultString += "\n{}".format(rsp["content"]["text"])
                            file['content']['cells'][L_c[1]]['outputs'].append(
                                {
                                    'name': rsp["content"]["name"], 
                                    'output_type': 'stream', 
                                    'text': rsp["content"]["text"]
                                },
                            )
                        elif msg_type == "execute_result":
                            if "image/png" in (rsp["content"]["data"].keys()):
                                S_resultString += "\n{}".format(rsp["content"]["data"]["image/png"])
                            else:
                                S_resultString += "\n{}".format(rsp["content"]["data"]["text/plain"])
                            if rsp["content"]["data"]["text/plain"] == '<IPython.core.display.Image object>':
                                file['content']['cells'][L_c[1]]['outputs'].append(
                                    {
                                        'name': "", 
                                        'output_type': 'stream', 
                                        'text': '尚未支援的格式，若有需求請通知工程組'
                                    },
                                )
                        elif msg_type == "display_data":
                            if rsp["content"]["data"].get("text/plain",None) != None:
                                S_resultString += "\n{}".format(rsp["content"]["data"])
                                file['content']['cells'][L_c[1]]['outputs'].append(
                                    {
                                        "output_type": "display_data",
                                        "data" : rsp["content"]['data'],
                                        "metadata": rsp["content"]['metadata']
                                    },
                                )
                        elif msg_type == "error":
                            S_resultString += "\n{}".format(rsp["content"]["traceback"])
                            B_hasFail = True
                            file['content']['cells'][L_c[1]]['outputs'].append(
                                {
                                    "output_type": "error",
                                    "ename" : rsp["content"]['ename'],
                                    "evalue": rsp["content"]['evalue'],
                                    "traceback": rsp["content"]['traceback'],
                                },
                            )

                        elif msg_type == "execute_reply" and rsp["content"]["status"] == "aborted":
                            S_resultString += "\n跳過"
                            file['content']['cells'][L_c[1]]['outputs'].append(
                                {
                                    'name': "stdout", 
                                    'output_type': 'stream', 
                                    'text': "因前方有錯誤，跳過"
                                },
                            )

                        elif msg_type == "status" and rsp["content"]["execution_state"] == "idle":
                            file['content']['cells'][L_c[1]]['outputs'].append(
                                {
                                    'output_type': 'display_data', 
                                    'data': {
                                        "text/html": airjobOutputInfo(S_dagID),
                                        "text/plain": ["<IPython.core.display.HTML object>"]
                                    },
                                    "metadata": {},
                                },
                            )
                            print(S_resultString)
                            break
                            
                except:
                    traceback.print_exc()
        except Exception as e:
            print('=== 錯誤訊息 ===')
            print(e)
            print('===============')
            try:
                ws.close()
            except:
                pass
            raise AirflowFailException("與Jupyter WebSocket連線失敗，請確認Token以及URL提供正確")
        print('所有Code已執行完畢')          
        ws.close()

        DeleteKernel(D_kernel['id'], D_AIRJOB_JupyterInfo['token'], D_AIRJOB_JupyterInfo['url'])

        new = {
            'type': "notebook",
            'content':file['content'],
        }
        print('更新Notebook')
        url = S_userJupyterUrl + '/api/contents' + notebook_path + "?token={}".format(S_jupyterToken)
        response = requests.put(url,data=json.dumps(new))
        if B_hasFail:
            raise AirflowFailException("Task Fail!")
        return B_hasFail

    elif S_fileType=='pyfile':
        try:
            print("開始啟動 WebSocket channels")
            S_ws_url = "ws://{}/api/kernels/".format(S_AIRJOBJupyter_ip_port)+D_kernel["id"]+"/channels?"+"token={}".format(D_AIRJOB_JupyterInfo['token'])
            ws = create_connection(
                S_ws_url)
            print('檢查kernel是否準備完畢')
            S_URL_CheckKernels = D_AIRJOB_JupyterInfo['url'] + '/api/kernels/{}?token={}'.format(D_kernel["id"],D_AIRJOB_JupyterInfo['token'])
            for i in range(60):
                response_checkKernels = requests.get(S_URL_CheckKernels)
                D_checkKernels = json.loads(response_checkKernels.text)
                if D_checkKernels['execution_state'] != 'starting':
                    print('確認kernel啟動完畢')
                    break
                time.sleep(1)
            else:
                ws.close()
                DeleteKernel(D_kernel['id'], D_AIRJOB_JupyterInfo['token'], D_AIRJOB_JupyterInfo['url'])
                raise AirflowFailException("Jupyter Kernel無法啟動成功")
        except Exception as e:
            print(e)
            try:
                ws.close()
            except:
                pass
            raise AirflowFailException("與Jupyter WebSocket連線失敗，請確認Token以及URL提供正確")

        B_hasFail = False   
        try:
            ws.send(json.dumps(send_execute_request('print("WebSocket Check")')))
            I_Try = 0
            while True and I_Try<20:
                rsp = json.loads(ws.recv())
                msg_type = rsp["msg_type"]
                if msg_type == "stream" and "WebSocket Check" in rsp["content"]["text"]:
                    break
                I_Try += 1
            else:
                ws.close()
                raise AirflowFailException("與Jupyter WebSocket溝通失敗，請通知工程組排除問題")
            I_Try = 0 
            while True and I_Try<20:
                rsp = json.loads(ws.recv())
                msg_type = rsp["msg_type"]
                if msg_type == "status" and rsp["content"]["execution_state"] == "idle":
                    break
                I_Try += 1
            else:
                ws.close()
                raise AirflowFailException("與Jupyter WebSocket溝通失敗，請通知工程組排除問題")




            print("code:\n================= START =================\n{}\n=================  END  =================".format(code))
            ws.send(json.dumps(send_execute_request(code)))
              
            I_inextGet = 0     
            S_resultString = "\n執行結果:"
            while True:
                I_inextGet += 1
                rsp = json.loads(ws.recv())
                msg_type = rsp["msg_type"]
                if msg_type == "stream":
                    S_resultString += "\n{}".format(rsp["content"]["text"])
                elif msg_type == "execute_result":
                    if "image/png" in (rsp["content"]["data"].keys()):
                        S_resultString += "\n{}".format(rsp["content"]["data"]["image/png"])
                    else:
                        S_resultString += "\n{}".format(rsp["content"]["data"]["text/plain"])
                elif msg_type == "display_data":
                    if rsp["content"]["data"].get("text/plain",None) != None:
                        S_resultString += "\n{}".format(rsp["content"]["data"])
                elif msg_type == "error":
                    S_resultString += "\n{}".format(rsp["content"]["traceback"])
                    B_hasFail = True
                elif msg_type == "execute_reply" and rsp["content"]["status"] == "aborted":
                    S_resultString += "\n跳過"
                elif msg_type == "status" and rsp["content"]["execution_state"] == "idle" and I_inextGet!=1:
                    print(S_resultString)
                    break
        except Exception as e:
            try:
                ws.close()
            except:
                pass
        
        print('所有Code已執行完畢')         
        ws.close()

        DeleteKernel(D_kernel['id'], D_AIRJOB_JupyterInfo['token'], D_AIRJOB_JupyterInfo['url'])
        
        if B_hasFail:
            raise AirflowFailException("Task Fail!")
        return B_hasFail

    
if __name__=='__main__':
    run("http://35.194.167.48:8001/notebooks/TestFloder/TestPyFile.ipynb","password")