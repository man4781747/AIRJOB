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
import logging

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
    "        <div class=\"airjob-infos-title\">?????????AIRJOB???????????????</div>\n",
    "        <div>????????????: {}</div>\n".format(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")),
    "        <a href='{url}' target=_blank>AIRJOB ??????:{url}</a>\n".format(url = S_airjobUrl.format(S_dagID.split('_')[0],S_dagID)),
    "    </div>\n",
    "</div>",
    ]
    return L_returnList

def connectWebSocket(S_Jupyter_ip_port, S_token, notebook_path):
    for retry in range(5):
        try:
            B_ok = False
            if retry != 0:
                logging.info('??????????????????: {}'.format(retry))
            S_kernelId = buildNewKernel(S_Jupyter_ip_port, S_token, notebook_path)
            S_ws_url = "ws://{}/api/kernels/{}/channels?token={}".format(
                S_Jupyter_ip_port,
                S_kernelId,
                S_token
            )
            logging.info("??????????????? WebSocket channels ??????")
            ws = create_connection(S_ws_url)
            logging.info('?????????????????????kernel??????????????????')
            S_URL_CheckKernels = 'http://{}/api/kernels/{}?token={}'.format(
                S_Jupyter_ip_port,
                S_kernelId,
                S_token
            )
            for i in range(60):
                response_checkKernels = requests.get(S_URL_CheckKernels)
                D_checkKernels = json.loads(response_checkKernels.text)
                if D_checkKernels['execution_state'] != 'starting':
                    logging.info('??????kernel????????????')
                    B_ok = True
                    break
                time.sleep(1)
            else:
                logging.info('Kernel??????timeout!')
                ws.close()
                DeleteKernel(S_kernelId, S_token, 'http://{}'.format(S_Jupyter_ip_port))
            if B_ok == False:
                continue
            
            logging.info('?????????WebSocket channels??????')
            ws.send(json.dumps(send_execute_request('print("WebSocket Check")')))
            S_returnSrt=""
            for I_Try in range(20):
                rsp = json.loads(ws.recv())
                S_returnSrt += '======\n{}\n======\n'.format(rsp)
                msg_type = rsp["msg_type"]
                if msg_type == "stream" and "WebSocket Check" in rsp["content"]["text"]:
                    break
                I_Try += 1
            else:
                ws.close()
                DeleteKernel(S_kernelId, S_token, 'http://{}'.format(S_Jupyter_ip_port))
                logging.error("???Jupyter WebSocket???????????????????????????:\n{}".format(S_returnSrt))
                
                continue
            I_Try = 0 
            S_returnSrt=""
            while True and I_Try<20:
                rsp = json.loads(ws.recv())
                S_returnSrt += '======\n{}\n======\n'.format(rsp)
                msg_type = rsp["msg_type"]
                if msg_type == "status" and rsp["content"]["execution_state"] == "idle":
                    break
                I_Try += 1
            else:
                ws.close()
                DeleteKernel(S_kernelId, S_token, 'http://{}'.format(S_Jupyter_ip_port))
                logging.error("???Jupyter WebSocket???????????????????????????:\n{}".format(S_returnSrt))
                continue

            logging.info('WebSocket ???????????? ????????????!')
            return (S_kernelId, ws)
        except Exception as e:
            logging.error('????????????????????????:{}'.format(str(e)))
            continue
    else:
        try:
            ws.close()
            DeleteKernel(S_kernelId, S_token, 'http://{}'.format(S_Jupyter_ip_port))
        except:
            pass
        raise ValueError("Jupyter Kernel??????????????????????????????????????????????????????????????????")


def DeleteKernel(S_kernelID, S_JuypterToken, S_JupyterURL):
    logging.info('????????????kernel: {}'.format(S_kernelID))
    S_URL_DelKernels = S_JupyterURL + '/api/kernels/{}?token={}'.format(S_kernelID,S_JuypterToken)
    for try_num in range(5):
        response = requests.delete(S_URL_DelKernels)
        logging.info(response.status_code)
        if response.status_code < 300:
            logging.info('??????kernel??????: {}'.format(S_kernelID))
            break
        logging.info('??????kernel?????????????????????: {}'.format(try_num))
    else:
        logging.info('??????kernel: {} ??????!!'.format(S_kernelID))

def buildNewKernel(S_Jupyter_ip_port, S_token, notebook_path):
    logging.info('?????????AIRJOB??????Jupyter??????')
    for retry in range(3):
        try:
            S_AIRJOB_JupyterRrl = "http://{}/api/sessions?token={}".format(S_Jupyter_ip_port,S_token)
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
            logging.info('??????session??????')
            response = requests.post(S_AIRJOB_JupyterRrl, data=params.encode('utf-8'))
            session = json.loads(response.text)
            D_kernel = session["kernel"]
            S_sessionsUuid = session['id']
            logging.info('?????????session??????: {}'.format(S_sessionsUuid))
            logging.info("??????kernel??????: {}".format(D_kernel['id']))
            return D_kernel['id']
        except Exception as e:
            logging.info('?????????Kernel???????????????: \n{}'.format(str(e)))
            logging.info('????????????: {}'.format(retry+1))
    else:
        raise ValueError("??????kernel???????????????????????????")

def run(S_jupyterNotebookUrl='', S_jupyterToken='', S_dagID=''):
    if S_jupyterNotebookUrl == '':
        raise ValueError("???jupyterNotebookUrl")
    if S_jupyterToken == '':
        raise ValueError("???jupyter Token")
    if S_dagID == '':
        raise ValueError("??? dagID")

    S_project = S_dagID.split('_')[0]
    if D_AIRJOB_Jupyter_metadata.get(S_project, None) == None:
        raise ValueError("?????????project: {} ?????????????????????????????????????????????".format(S_project))

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
        logging.info('URL Format ??????')
        logging.info(S_jupyterNotebookUrl)
        raise ValueError("URL ??????????????????????????????")

    logging.info('????????????Jupyter??????: {}'.format(S_jupyterNotebookUrl))

    notebook_path = '/' + Re_jupyterNotebookUrl.group('notebook_path').split('?')[0].split('#')[0]
    S_userJupyterUrl = Re_jupyterNotebookUrl.group('jupyter_url')

    #??????Jupyter?????????????????????
    try:
        logging.info("??????notebook????????????????????????Cell??????Code")
        url = S_userJupyterUrl + '/api/contents' + notebook_path + "?token={}".format(S_jupyterToken)
        response = requests.get(url)
        file = json.loads(response.text)
        if file['type'] == "notebook":
            S_fileType = 'notebook'
            logging.info('?????????Notebook??????')
            code = [ [c['source'],index] for index,c in enumerate(file['content']['cells']) if c['cell_type']=='code' if len(c['source'])>0 ]   
        elif file['type'] == "file" and file['mimetype'] == "text/x-python":
            S_fileType = 'pyfile'
            logging.info('?????????.py??????')
            code = file['content']
        else:
            raise ValueError("??????????????????")
    except Exception as e:
        logging.info(e)
        raise ValueError("??????NoteBook????????????????????????Token??????URL????????????")

    #??????name???uuid_?????????Kernels?????????idle??????last_activity??????5????????????session??????????????????(???????????????????????????????????????kernel)
    try:
        logging.info('????????????AIRJOB??????Jupyter?????????Kernels')
        # D_AIRJOB_JupyterInfo = D_AIRJOB_Jupyter_metadata[S_project]
        # S_sessions_url = D_AIRJOB_JupyterInfo['url'] + "/api/sessions?token={}".format(D_AIRJOB_JupyterInfo['token'])
        S_sessions_url = S_userJupyterUrl + "/api/sessions?token={}".format(S_jupyterToken)

        response_Kernels = requests.get(S_sessions_url)
        L_Sessions = json.loads(response_Kernels.text)
        for D_sessionInfo in L_Sessions:
            if D_sessionInfo.get('name',"xxxxxxxx")[:5] != 'uuid_':
                # ????????????uuid_?????????session
                continue
            try:
                DT_last_activity = datetime.datetime.strptime(D_sessionInfo.get('last_activity',''),"%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(hours=8)
                if DT_last_activity > (datetime.datetime.now() - datetime.timedelta(minutes=5)):
                    # ??????last_activity??????5????????????kernel
                    continue
            except Exception as e:
                logging.info('???????????? last_activity: {}'.format(e))
            if D_sessionInfo.get('kernel',{}).get('execution_state','no') not in ['idle', 'starting']:
                # ??????execution_state??????idle???kernel
                continue

            logging.info('?????????????????????kernel')
            if D_sessionInfo['kernel']['execution_state'] == 'starting':
                logging.info('??????????????????5???????????????????????????kernel')
            S_kernel_id = D_sessionInfo['kernel']['id']

            # DeleteKernel(S_kernel_id, D_AIRJOB_JupyterInfo['token'], D_AIRJOB_JupyterInfo['url'])
            DeleteKernel(S_kernel_id, S_jupyterToken, S_sessions_url)
        logging.info('???????????????Kernels??????!')
    except Exception as e:
        logging.info('???????????????Kernels??????! {}'.format(e))

    # D_AIRJOB_JupyterInfo = D_AIRJOB_Jupyter_metadata[S_project]
    # S_AIRJOBJupyter_ip_port = D_AIRJOB_JupyterInfo['url'].split('//')[-1]

    #?????????AIRJOB??????Jupyter??????

    (S_kernelId, ws) = connectWebSocket(
        S_userJupyterUrl.split("//")[-1],
        S_jupyterToken,
        notebook_path
    )


    if S_fileType=='notebook':
        B_hasFail = False   
        try:
            logging.info('??????????????????')
            for I_inedx,L_c in enumerate(code):
                logging.info(
                    '\n?????????{}?????????code:\n================= START =================\n{}\n=================  END  ================='.format(
                    L_c[1]+1,
                    L_c[0])
                )

                ws.send(json.dumps(send_execute_request(L_c[0])))
                try:
                    msg_type = ''
                    S_resultString = "\n????????????:"
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
                                        'text': '??????????????????????????????????????????????????????'
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
                            S_resultString += "\n??????"
                            file['content']['cells'][L_c[1]]['outputs'].append(
                                {
                                    'name': "stdout", 
                                    'output_type': 'stream', 
                                    'text': "???????????????????????????"
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
                            logging.info(S_resultString)
                            break
                            
                except:
                    traceback.print_exc()
        except Exception as e:
            logging.info('=== ???????????? ===')
            logging.info(e)
            logging.info('===============')
            try:
                ws.close()
            except:
                pass
            raise ValueError("???Jupyter WebSocket????????????????????????Token??????URL????????????")
        logging.info('??????Code???????????????')          
        ws.close()

        DeleteKernel(S_kernelId, D_AIRJOB_JupyterInfo['token'], D_AIRJOB_JupyterInfo['url'])

        new = {
            'type': "notebook",
            'content':file['content'],
        }
        logging.info('??????Notebook')
        url = S_userJupyterUrl + '/api/contents' + notebook_path + "?token={}".format(S_jupyterToken)
        response = requests.put(url,data=json.dumps(new))
        if B_hasFail:
            raise ValueError("Task Fail!")
        return B_hasFail

    elif S_fileType=='pyfile':
        B_hasFail = False   
        try:
            logging.info('??????????????????')
            logging.info("code:\n================= START =================\n{}\n=================  END  =================".format(code))
            ws.send(json.dumps(send_execute_request(code)))
            I_inextGet = 0     
            S_resultString = "\n????????????:"
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
                    S_resultString += "\n??????"
                elif msg_type == "status" and rsp["content"]["execution_state"] == "idle" and I_inextGet!=1:
                    logging.info(S_resultString)
                    break
        except Exception as e:
            try:
                ws.close()
            except:
                pass
        
        logging.info('??????Code???????????????')         
        ws.close()

        DeleteKernel(S_kernelId, D_AIRJOB_JupyterInfo['token'], D_AIRJOB_JupyterInfo['url'])
        
        if B_hasFail:
            raise ValueError("Task Fail!")
        return B_hasFail

    
if __name__=='__main__':
    run("http://35.194.167.48:8001/notebooks/TestFloder/TestPyFile.ipynb","password")