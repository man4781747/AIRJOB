import os
import json

class dagSettingFileManager:
    # def __init__(self, S_filePath):
        # self.S_filePath = S_filePath
        
    def BuildNewDagSettingFile(self, S_filePath,D_settingData):
        self.S_filePath = S_filePath
        with open(S_filePath, 'w', encoding='utf-8') as f:
            S_jsonStr = json.dumps(D_settingData, indent=4)
            f.write(S_jsonStr)
            
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
    
