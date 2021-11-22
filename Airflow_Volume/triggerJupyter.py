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

S_airjobUrl = "http://35.194.167.48:8000/AirFlowUploadWeb/testHTML/{}/?Page=dagInfoView&dag_id={}&SheetChose=DAG_Infomation"

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

    #先在有開Spark UI的Jupyter內獲得檔案內容
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

    #準備與AIRJOB專用Jupyter連線
    try:
        print('準備與AIRJOB專用Jupyter連線')
        D_AIRJOB_JupyterInfo = D_AIRJOB_Jupyter_metadata[S_project]
        S_AIRJOB_JupyterRrl = D_AIRJOB_JupyterInfo['url'] + "/api/sessions?token={}".format(D_AIRJOB_JupyterInfo['token'])
        S_AIRJOBJupyter_ip_port = D_AIRJOB_JupyterInfo['url'].split('//')[-1]
        print(S_AIRJOB_JupyterRrl)
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
            B_hasFail = False    

            L_resultList = []
            # 嘗試處裡Jupyter API的錯位BUG
            print('嘗試與Jupyter溝通並檢查類型')
            msg_type = ''
            ws.send(json.dumps(send_execute_request(code[0][0])))
            rsp = json.loads(ws.recv())
            msg_type = rsp["msg_type"]
            I_shift = 0
            if msg_type == "status" and rsp["content"]["execution_state"] == "idle":
                print('會位移的類型，嘗試修正')
                code = code + [['',-1]]
                ws.send(json.dumps(send_execute_request(code[1][0])))
                I_shift = 1
            else:
                print('不會位移的類型')
                while True:
                    rsp = json.loads(ws.recv())
                    msg_type = rsp["msg_type"]
                    if msg_type == "status" and rsp["content"]["execution_state"] == "idle":
                        break
            print('開始執行程式')
            for I_inedx,L_c in enumerate(code):
                if L_c[1] != -1:
                    print(
                        '\n執行第{}區塊的code:\n================= START =================\n{}\n=================  END  ================='.format(
                        L_c[1]+1,
                        L_c[0])
                    )
                else:
                    break
                if I_shift != 1 or I_inedx not in [1,0] :
                    ws.send(json.dumps(send_execute_request(L_c[0])))
                try:
                    msg_type = ''
                    S_resultString = "\n執行結果:"
                    file['content']['cells'][L_c[1]]['outputs'] = []
                    while True:
                        rsp = json.loads(ws.recv())
                        msg_type = rsp["msg_type"]
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
                            if L_c[1] != -1:
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
        ws.close()
        print('刪除kernel: {}'.format(D_kernel['id']))
        S_URL_DelKernels = D_AIRJOB_JupyterInfo['url'] + '/api/kernels/{}?token={}'.format(D_kernel['id'],D_AIRJOB_JupyterInfo['token'])
        response = requests.delete(S_URL_DelKernels)
        print(response)
        print('刪除kernel成功: {}'.format(D_kernel['id']))
        # print('刪除session: {}'.format(S_sessionsUuid))
        # S_URL_DelSession = base + '/api/sessions/{}?token={}'.format(S_sessionsUuid,S_jupyterToken)
        # response = requests.delete(S_URL_DelSession,headers=headers)
        # print(response)
        # print('刪除session成功: {}'.format(S_sessionsUuid))
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
            print("code:\n================= START =================\n{}\n=================  END  =================".format(code))
            ws.send(json.dumps(send_execute_request(code)))
            B_hasFail = False  
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
        print('刪除kernel: {}'.format(D_kernel['id']))
        S_URL_DelKernels = D_AIRJOB_JupyterInfo['url'] + '/api/kernels/{}?token={}'.format(D_kernel['id'],D_AIRJOB_JupyterInfo['token'])
        response = requests.delete(S_URL_DelKernels)
        print(response)
        print('刪除kernel成功: {}'.format(D_kernel['id']))
        
        if B_hasFail:
            raise AirflowFailException("Task Fail!")
        return B_hasFail

    
if __name__=='__main__':
    run("http://35.194.167.48:8001/notebooks/TestFloder/TestPyFile.ipynb","password")