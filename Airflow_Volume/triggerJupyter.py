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

def run(S_jupyterNotebookUrl, S_jupyterToken):
    try:
        S_jupyterToken = tokenTransform.dectry(S_jupyterToken)
    except:
        pass

    Re_jupyterNotebookUrl = re.search(r"^(?P<jupyter_url>.*)/notebooks/(?P<notebook_path>.*)", S_jupyterNotebookUrl)
    if not Re_jupyterNotebookUrl:
        print('URL Format 錯誤')
        print(S_jupyterNotebookUrl)
        raise AirflowFailException("URL 格式錯誤，找不到檔案")
    
    try:
        notebook_path = '/' + Re_jupyterNotebookUrl.group('notebook_path') 
        base = Re_jupyterNotebookUrl.group('jupyter_url')
        headers = {'Authorization': S_jupyterToken}
        S_ip_port = base.split('//')[-1]
        
        url = base + '/api/sessions' + "?token={}".format(S_jupyterToken)

        params = '{"path":\"%s\","type":"notebook","name":"","kernel":{"id":null,"name":"python3"}}' % notebook_path
        response = requests.post(url, headers=headers, data=params)
        session = json.loads(response.text)
        kernel = session["kernel"]
    except Exception as e:
        raise AirflowFailException("登入Jupyter失敗，請確認Token以及URL提供正確")

    try:
        # 讀取notebook檔案，並獲取每個Cell裡的Code
        url = base + '/api/contents' + notebook_path + "?token={}".format(S_jupyterToken)
        response = requests.get(url,headers=headers)
        file = json.loads(response.text)
        code = [ [c['source'],index] for index,c in enumerate(file['content']['cells']) if len(c['source'])>0 ]   
    except Exception as e:
        raise AirflowFailException("獲得NoteBook內容失敗，請確認Token以及URL提供正確")

    try:
        # 開始啟動 WebSocket channels (request/reply)
        S_ws_url = "ws://{}/api/kernels/".format(S_ip_port)+kernel["id"]+"/channels?session_id"+session["id"] + "&token={}".format(S_jupyterToken)
        ws = create_connection(
            S_ws_url, 
            header=headers)
        for L_c in code:
            ws.send(json.dumps(send_execute_request(L_c[0])))
    except Exception as e:
        try:
            ws.close()
        except:
            pass
        raise AirflowFailException("與Jupyter WebSocket連線失敗，請確認Token以及URL提供正確")

    # 我們只拿Code執行完的訊息結果，其他訊息將被忽略
    B_hasFail = False
    for i in range(0, len(code)+1):
        try:
            msg_type = ''
            while True:
                rsp = json.loads(ws.recv())
                msg_type = rsp["msg_type"]
                if msg_type == "stream":
                    print(rsp["content"]["text"])
                    file['content']['cells'][code[i-1][1]]['outputs'] = [
                        {
                        'name': 'stdout', 
                        'output_type': 'stream', 
                        'text': "===== 以下由AIRJOB觸發並更新 =====\n===== 觸發時間: {}\n".format(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f"))
                        },
                        {
                        'name': rsp["content"]["name"], 
                        'output_type': 'stream', 
                        'text': rsp["content"]["text"]
                        },
                    ]
                elif msg_type == "execute_result":
                    if "image/png" in (rsp["content"]["data"].keys()):
                        print(rsp["content"]["data"]["image/png"])
                    else:
                        print(rsp["content"]["data"]["text/plain"])
                elif msg_type == "display_data":
                    print(rsp["content"]["data"]["image/png"])
                    file['content']['cells'][code[i-1][1]]['outputs'] = [                        
                        {
                        'name': 'stdout', 
                        'output_type': 'stream', 
                        'text': "===== 以下由AIRJOB觸發並更新 =====\n===== 觸發時間: {}\n".format(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f"))
                        },
                        {
                        "output_type": "display_data",
                        "data" : rsp["content"]['data'],
                        "metadata": rsp["content"]['metadata']
                        }
                    ]
                elif msg_type == "error":
                    print(rsp["content"]["traceback"])
                    B_hasFail = True
                    file['content']['cells'][code[i-1][1]]['outputs'] = [                        
                        {
                        'name': 'stdout', 
                        'output_type': 'stream', 
                        'text': "===== 以下由AIRJOB觸發並更新 =====\n===== 觸發時間: {}\n".format(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f"))
                        },
                        {
                        "output_type": "error",
                        "ename" : rsp["content"]['ename'],
                        "evalue": rsp["content"]['evalue'],
                        "traceback": rsp["content"]['traceback'],
                        }
                    ]

                elif msg_type == "execute_reply" and rsp["content"]["status"] == "aborted":
                    print("跳過")
                    file['content']['cells'][code[i-1][1]]['outputs'] = [                        
                        {
                        'name': 'stdout', 
                        'output_type': 'stream', 
                        'text': "===== 以下由AIRJOB觸發並更新 =====\n===== 因上方錯誤，跳過\n".format(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f"))
                        },
                    ]

                elif msg_type == "status" and rsp["content"]["execution_state"] == "idle":
                    break
                    

        except:
                traceback.print_exc()
                ws.close()
                
    ws.close()

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