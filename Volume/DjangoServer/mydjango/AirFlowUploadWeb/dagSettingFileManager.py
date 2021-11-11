import os
import json
import sys
sys.path.append(os.path.split(os.path.realpath(__file__))[0])
import tokenTransform


class dagSettingFileManager:
    # def __init__(self, S_filePath):
        # self.S_filePath = S_filePath
        
    def BuildNewDagSettingFile(self, S_filePath,D_settingData):
        try:
            self.S_filePath = S_filePath

            ##########################################################
            for S_taskUuid in D_settingData['TaskSettingList'].keys():
                if D_settingData['TaskSettingList'][S_taskUuid]['type'] == "PythonOperator":
                    try:
                        tokenTransform.dectry(
                            D_settingData['TaskSettingList'][S_taskUuid]['jupyter_token']
                        )
                    except:
                        D_settingData['TaskSettingList'][S_taskUuid]['jupyter_token'] = tokenTransform.enctry(
                            D_settingData['TaskSettingList'][S_taskUuid]['jupyter_token']
                        )
            ##########################################################

            with open(S_filePath, 'w', encoding='utf-8') as f:
                S_jsonStr = json.dumps(D_settingData, indent=4)
                f.write(S_jsonStr)
            return D_settingData
        except:
            raise BaseException("BuildNewDagSettingFile Error")
    def LoadDagSettingFile(self, S_filePath):
        self.S_filePath = S_filePath
        if not os.path.exists(S_filePath):
            print("don't exists: {}".format(S_filePath))
            self.D_dagSetting = {}
            return self.D_dagSetting
            
        with open(S_filePath, 'r', encoding='utf-8') as f:
            self.D_dagSetting = json.loads(f.read())
        return self.D_dagSetting
    
    def SaveDagSettingFile(self):
        with open(self.S_filePath, 'w', encoding='utf-8') as f:
            S_jsonStr = json.dumps(self.D_settingData, indent=4)
            f.write(S_jsonStr)
    
