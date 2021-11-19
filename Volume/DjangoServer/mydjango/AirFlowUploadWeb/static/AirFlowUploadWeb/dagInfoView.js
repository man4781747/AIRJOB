Vue.component("file-manager-tree", {
    template:`
		<div>
			<div class='file-manager-folder-name'
				:style="files.folderName==folder_chose?'background-color:gray':''"
			>
				<i @click='files.ifOpen = !files.ifOpen' v-if='files.ifOpen' class="far fa-folder-open"></i>
				<i @click='files.ifOpen = !files.ifOpen' v-else class="far fa-folder"></i>
				<div @click=''
					@dblclick='folderClick()'
				>{{files.folderName}}</div>
			</div>
			<div 
				class='file-manager-chil-folders' 
				v-for="(folderItem, folderName, index) in files.folders"
				v-show='files.ifOpen'
			>
				<file-manager-tree
					v-bind:files="folderItem"
					v-bind:folder_chose="folder_chose"
				></file-manager-tree>
			</div>
		</div>
    `,
	data: function(){
		return {
			message: 'Hello',
			
		}
	},
    props: ['files','folder_chose', 'parent_folder'],
    methods: {
		folderClick(){
			// VueSetting.folderChose = this.files.folderName
			// VueSetting.folderChoseItem = this.files
			VueSetting.clickFileMangerFolderOnTable(this.files.folderName, this.files)
		},
	},
	computed: {
		parentFolder: function(){
			return this
		},
	},
	created: function() { 
	},



})


var VueSetting_dagInfoView = {
	data: {
		DAGSettingInfo : {},
		DAGDetailOpen: '',
		SheetChose: 'DAG_Infomation',
		DagRunIDChosed: '',
		updateDAGSettingInfo: false,
		updateSourceCode: false,
		fileWindowWidth: 100,
		folderChose: '',
		folderChoseItem: {},
		filePathList : [],
		delFilePathList : [],
		delFileFetch : [],
		deleteCheckWindowShow : false,
		AllCheckBox : false,

		dagRunHistoryStatus: 'Close',

		dagTaskSelecterOpen: false,

		dagRunHistoryChose: {},
		dagRunHistoryTaskIndexChose: null,
		dagRunHistoryLogContentChose: -1,
		logDataRequestNum: '',
		dagRunIDOpen: '',

		deleteDAGCheckWindowShow: false,
	},
  
	computed: {
		dagRunHistoryTaskIdChose(){
			try{
				if (this.dagRunHistoryChose[this.dagRunHistoryTaskIndexChose] != undefined){
					return this.dagRunHistoryChose[this.dagRunHistoryTaskIndexChose]
				}
				return {}
			}
			catch{return {}}
		},
		getChosedFiles(){
			if (this.folderChoseItem['files'] == undefined){
				return []
			}
			var returnList = []
			for (fileName of Object.keys(this.folderChoseItem['files'])){
				if (this.folderChoseItem['files'][fileName]['chosed']){
					returnList.push(this.folderChoseItem['files'][fileName]['fullPath'])
				}
			}
			for (folderName of Object.keys(this.folderChoseItem['folders'])){
				if (this.folderChoseItem['folders'][folderName]['chosed']){
					returnList.push(this.folderChoseItem['folders'][folderName]['fullPath'])
				}
			}

			return returnList
		},

		AllCheckBoxValue(){
			if (this.folderChoseItem['files'] == undefined | this.folderChoseItem['folders']){
				return false
			}

			for (fileName of Object.keys(this.folderChoseItem['files'])){
				if (this.folderChoseItem['files'][fileName]['chosed'] == false){
					return false
				}
			}
			for (folderName of Object.keys(this.folderChoseItem['folders'])){
				if (this.folderChoseItem['folders'][folderName]['chosed'] == false){
					return false
				}
			}

			return true
		},
	},
  
	methods: {
		DAGDetailSheetClick(S_sheetChose){
			this.SheetChose = S_sheetChose
			this.urlParas['SheetChose'] = S_sheetChose
			this.updateUrlParas()
		},

		clickDAGRunIDRow(dag_run_id){
			var dag_run_id = dag_run_id

			this.urlParas['dag_run_id'] = dag_run_id
			this.updateUrlParas()

			this.dagRunHistoryStatus = 'Update'
			var uuid_this_requests = _uuid()
			this.logDataRequestNum = uuid_this_requests

			uploadFetch = fetch('/AirFlowUploadWeb/API/v1/GetDAGRunLogByRunID/'+this.DAGDetailOpen+'/'+dag_run_id+'/', {
			}).then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				// console.log(myJson);
				// console.log(uuid_this_requests);
				if (VueSetting.logDataRequestNum == uuid_this_requests){
					// Vue.set(
					// 	VueSetting.DAGList[VueSetting.DAGDetailOpen].dagRuns.total[dag_run_id],
					// 	'Logs',
					// 	myJson['result']['task_instances']
					// )
					VueSetting.dagRunHistoryStatus = 'Open'
					VueSetting.dagRunHistoryTaskIndexChose = null
					VueSetting.dagRunHistoryLogContentChose = 0,
					VueSetting.dagRunIDOpen = dag_run_id
					VueSetting.dagRunHistoryChose = myJson['result']['task_instances']
					for (D_runInfoChose of myJson['result']['task_instances']){
						if (D_runInfoChose.state == undefined){
							console.log('持續更新 : '+dag_run_id)
							VueSetting.autoUploadDAGRunInfo(dag_run_id)
							break
						}
					}

				}
			})
		},

		uploadDAGRunInfo(dag_run_id){
			var dag_run_id = dag_run_id
			var uuid_this_requests = _uuid()
			this.logDataRequestNum = uuid_this_requests

			uploadFetch = fetch('/AirFlowUploadWeb/API/v1/GetDAGRunLogByRunID/'+this.DAGDetailOpen+'/'+dag_run_id+'/', {
			}).then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				if (VueSetting.dagRunIDOpen == dag_run_id){
					Vue.set(
						VueSetting.DAGList[VueSetting.DAGDetailOpen].dagRuns.total[dag_run_id],
						'Logs',
						myJson['result']['task_instances']
					)
					VueSetting.dagRunHistoryChose = myJson['result']['task_instances']
					for (D_runInfoChose of myJson['result']['task_instances']){
						if (D_runInfoChose.state == undefined){
							console.log('持續更新 : '+dag_run_id)
							VueSetting.autoUploadDAGRunInfo(dag_run_id)
							break
						}
					}
				}
			});
		},

		autoUploadDAGRunInfo(dag_run_id){
			var dag_run_id = dag_run_id
			uploadFetch = fetch('/AirFlowUploadWeb/API/v1/GetDAGRunLogByRunID/'+this.DAGDetailOpen+'/'+dag_run_id+'/', {
			}).then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				if (VueSetting.dagRunIDOpen == dag_run_id){
					Vue.set(
						VueSetting.DAGList[VueSetting.DAGDetailOpen].dagRuns.total[dag_run_id],
						'Logs',
						myJson['result']['task_instances']
					)
					VueSetting.dagRunHistoryChose = myJson['result']['task_instances']
					for (D_runInfoChose of myJson['result']['task_instances']){
						if (D_runInfoChose.state == undefined){
							setTimeout(function() {
								console.log('持續更新 : '+dag_run_id)
								VueSetting.autoUploadDAGRunInfo(dag_run_id)
							}, 1000);
							break
						}
					}
				}
				else{console.log('停止更新 : '+dag_run_id)}
			});
		},

		closeDagLogWindow(){
			this.dagRunHistoryStatus = 'Close'
			this.dagRunHistoryTaskIndexChose = null
			this.dagRunHistoryLogContentChose = 0,
			this.dagRunHistoryChose = {}
			this.logDataRequestNum = ''
			this.dagRunIDOpen = ''
		},

		closeDagDetailWindow(){
			this.urlParas = {
				'Page': "dagListViewer",
			}
			this.updateUrlParas()

			this.NowPage="dagListViewer"
			this.closeDagLogWindow()
			this.SheetChose="DAG_Infomation"
			this.getDAGList()
		},

		// 更新 DAG Infomation 頁面內容
		loadExistDAGSettingInfo(S_dag_id){
			// let params = new FormData();
			// params.append("DAG_ID", S_dag_id)
			this.updateDAGSettingInfo = true

			this.DAGSettingInfo = {
				'SysInfo' : 'Loading',
				'DAG_ID' : S_dag_id,
			}
			console.log("/AirFlowUploadWeb/API/v1/"+this.projectName+"/loadExistDAGSettingInfo/"+S_dag_id+"/")
			fetch("/AirFlowUploadWeb/API/v1/"+this.projectName+"/loadExistDAGSettingInfo/"+S_dag_id+"/", {
			}).then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				if (myJson['Warning'] != undefined){
					VueSetting.DAGSettingInfo = {
						'SysInfo' : 'Warning',
						'DAG_ID' : S_dag_id,
						'Message' : myJson['Warning'],
					}
				}
				else {
					VueSetting.DAGSettingInfo = {
						'SysInfo' : 'Success',
						'DAG_ID' : S_dag_id,
						'DAGDetailInfo' : myJson,
					}
				}
				VueSetting.updateDAGSettingInfo = false
			})
		},
		
		// 更新Source Code 頁面內容
		getDAGContent(S_dagID){
			this.updateSourceCode = false
			fetch("/AirFlowUploadWeb/API/v1/"+this.projectName+"/GetDAGSourseCode/"+S_dagID+"/", {
			}).then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				Vue.set(
					VueSetting.DAGList[S_dagID],
					'content',
					myJson['result']
				)
				VueSetting.updateSourceCode = false
				// console.log(myJson)
			})
		},

		// 更新 Runs History 頁面內容
		uploadDAGRunsInfoByDagId(S_dagID){
			let params = new FormData();
			// console.log(S_dagID)
			Vue.set(
				this.DAGList[S_dagID],
				'updateRunsList',
				true
			)

			params.append("DAG_ID", S_dagID)
			fetch("/AirFlowUploadWeb/GetDAGRunsList/", {
				method: 'POST',
				body: params,
			}).then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				// console.log(myJson)
				if (myJson['DAG_Runs'] != undefined){
					let DAG_RunsList = {
						'total' : {},
						'groups' : {}
					}
					for (D_runInfo of myJson['DAG_Runs']['dag_runs']){
						DAG_RunsList['total'][D_runInfo.dag_run_id] = D_runInfo
					}


					// let DAG_RunsList = {
					// 	'total' : myJson['DAG_Runs']['dag_runs'],
					// 	'groups' : {}
					// }
					VueSetting.DAGList[S_dagID]['updateRunsList'] = false
					Vue.set(
						VueSetting.DAGList[S_dagID],
						'dagRuns',
						DAG_RunsList
					)
				} else {
					console.log('Upload Fail')
					// console.log(myJson)
				}
			})
		},

		// 更新 FileManager 頁面內容
		getFileManagerInfoByDAGId(S_dagID){
			console.log('更新 FileManager 頁面內容')
			fetch("/AirFlowUploadWeb/API/v1/"+this.projectName+"/GetFilesInDAGFolder/"+S_dagID+"/", {
			}).then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				function setIfOpenPara(D_folderInfo, D_parentFolder) {
					D_folderInfo['parentFolder'] = D_parentFolder

					if (Object.keys(D_folderInfo.folders).length == 0){
						D_folderInfo['ifOpen'] = true
					} else {
						D_folderInfo['ifOpen'] = false
					}

					for (S_fileName of Object.keys(D_folderInfo.files)){
						D_folderInfo.files[S_fileName]['chosed'] = false
					}
					for (S_folderName of Object.keys(D_folderInfo.folders)){
						D_folderInfo.folders[S_folderName]['chosed'] = false
						setIfOpenPara(D_folderInfo.folders[S_folderName], D_folderInfo)
					}

				}
				// console.log(myJson)
				setIfOpenPara(myJson['folderInfo'], null)

				Vue.set(
					VueSetting.DAGList[S_dagID],
					'fileManager',
					myJson['folderInfo']
				)
			
				VueSetting.openFileMangerFolderByPathList(VueSetting.filePathList, S_dagID)
				VueSetting.fileTreeInfo = myJson['folderInfo']
				VueSetting.fileTreeFolderChosed = myJson['folderInfo']['folderName']

				// console.log(myJson)
			})
		},

		// 打開 DAGEditer 頁面(修改模式)
		openDAGEditerWithDAGSettingInfo(){
			this.DAG_ID_locker = true
			this.dagIdCheckPass = true
			this.lastPage = "dagInfoView"
			console.log(this.DAGSettingInfo['DAGDetailInfo'])
			this.SetEditer(this.DAGSettingInfo['DAGDetailInfo'])
			this.openDAGEditer()
		},
		
		UpdateAllSheetInfo(){
			this.getDAGContent(this.DAGDetailOpen)
			this.loadExistDAGSettingInfo(this.DAGDetailOpen)
			this.getFileManagerInfoByDAGId(this.DAGDetailOpen)
		},

		UpdateDAGSettingButtonClick(){
			this.uploadNewDAGSettingInfoToServer().then(function(myJson){
				console.log('獲得上傳的回應，重新讀取所有Sheet訊息，並跳回dagInfoView視窗')
				VueSetting.getDAGList()
				VueSetting.NowPage = "dagInfoView"
			})
		},

		resizeColWindow(event){
			var mouse_X = event.screenX
			document.onmousemove = function(ev){
				let oEvent = ev || event
				var mouse_New = oEvent.screenX

				let widthChange = mouse_New - mouse_X
				VueSetting.fileWindowWidth = VueSetting.fileWindowWidth + widthChange
				if (VueSetting.fileWindowWidth <= 50) {
					VueSetting.fileWindowWidth = 50
				}
				mouse_X = mouse_New
			}
			document.onmouseup = function(){
				document.onmousemove = null
				document.onmouseup = null
			}
		},

		trigerDeleteDAG(DAG_ID){
			fetch("/AirFlowUploadWeb/API/v1/"+this.projectName+"/DeleteDAG/"+DAG_ID+"/", {
				method: 'DELETE',
			}).then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				console.log(myJson);
				VueSetting.deleteDAGCheckWindowShow=false
				VueSetting.clickHomeBtn()
			})
		},

		clickTaskIdOption(index){
			this.dagRunHistoryTaskIndexChose = index
			this.dagRunHistoryLogContentChose = 0
		},

		clickDeleteDAGButton(){
			this.deleteDAGCheckWindowShow = true
		},

		clickAllCheckBox(){
			let setValue = !this.AllCheckBoxValue
			for (fileName of Object.keys(this.folderChoseItem['files'])){
				this.folderChoseItem['files'][fileName]['chosed'] = setValue
			}
			for (folderName of Object.keys(this.folderChoseItem['folders'])){
				this.folderChoseItem['folders'][folderName]['chosed'] = setValue
			}

		},

		clickFileMangerFolderOnTable(folderName, folderItem){
			this.folderChose = folderName
			this.folderChoseItem = folderItem
			// this.closeAllChildFolder(folderItem)
			this.openAllParentFolder(folderItem)
		},

		clickDeleteAllChosedFileButtom(){
			this.delFilePathList = this.getChosedFiles.slice(0)
			if (this.delFilePathList.length != 0){
				this.deleteCheckWindowShow = true
			}
		},

		openFileMangerFolderByPathList(PathList, S_dagID){
			var folderChose = this.DAGList[S_dagID].fileManager
			if (folderChose.folderName != PathList[0]){
				this.clickFileMangerFolderOnTable(folderChose.folderName, folderChose)
				return null
			} else if (PathList.length<2) {
				this.clickFileMangerFolderOnTable(folderChose.folderName, folderChose)
				return null
			}
			for (S_folderName of PathList.slice(1)){
				if (folderChose['folders'][S_folderName] != undefined){
					folderChose = folderChose['folders'][S_folderName]
				} else {break}
			}
			this.clickFileMangerFolderOnTable(folderChose.folderName, folderChose)
			return null
		},

		openAllParentFolder(folderItem){
			this.filePathList = []
			while (folderItem != null){
				// console.log('Open folder: '+folderItem['folderName'])
				this.filePathList.push(folderItem['folderName'])
				folderItem.ifOpen = true
				folderItem = folderItem.parentFolder
			}
			this.filePathList.reverse()
		},

		deleteAllChosedFile(ChosedFileList){
			// this.getChosedFiles
			this.delFileFetch = []
			for (S_filePathChose of ChosedFileList){
				fetchResult = this.deleteUploadedFile(S_filePathChose)
				this.delFileFetch.push(fetchResult)
			}
			this.deleteCheckWindowShow = false
		},

		deleteUploadedFile(S_fileFullPath){
			let params = new FormData();
			params.append("fileFullPath", S_fileFullPath)
			fetchResult = fetch("/AirFlowUploadWeb/DeleteUploadedFile/", {
				method: 'POST',
				body: params,
			}).then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				// console.log(myJson)
				if (myJson['Result']=='Success'){
					Vue.delete(VueSetting.folderChoseItem.files, myJson['File']);
					Vue.delete(VueSetting.folderChoseItem.folders, myJson['Folder']);
				}
				return myJson
			})
			return fetchResult
		},

		closeAllChildFolder(folderItem){
			folderItem.ifOpen = false
			for (folderName of Object.keys(folderItem.folders)){
				this.closeAllChildFolder(folderItem.folders[folderName])
			}
		},

		makeZipFile(){
			// console.log(this.getChosedFiles)
			if (this.getChosedFiles.length==0){
				return null
			}

			var Form = new FormData();
			Form.append('FileList', this.getChosedFiles)

			uploadFetch = fetch('/AirFlowUploadWeb/MakeZipFile/', {
				method: 'POST',
				body: Form,
			}).then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				// console.log(myJson);
				if (myJson['Result'] == 'Success'){
					console.log('makeZipFile 成功， 準備下載')
					VueSetting.downloadZipFile(myJson['key'])
				}
			});
		},

		downloadZipFile(key){
			var myHeaders = new Headers();
			var key = key
			myHeaders.append('key', key)
			uploadFetch = fetch('/AirFlowUploadWeb/DownloadZipFile/', {
				method: 'GET',
				headers: myHeaders,
			}).then(function(response) {
				return response.blob();
			})
			.then(function(blob) {
				var url = window.URL.createObjectURL(blob);
				var a = document.createElement('a');
				a.href = url;
				a.download = key+'.zip';
				document.body.appendChild(a); // we need to append the element to the dom -> otherwise it will not work in firefox
				a.click();    
				a.remove();
				console.log('downloadZipFile 成功， 準備刪除')
				VueSetting.deleteZipFile(key)
			})
			.catch(reason => {
				console.error( 'onRejected function called: ', reason );
			})
		},

		deleteZipFile(key){
			var myHeaders = new Headers();
			var key = key
			myHeaders.append('key', key)
			uploadFetch = fetch('/AirFlowUploadWeb/DeleteZipFile/', {
				method: 'GET',
				headers: myHeaders,
			}).then(function(response) {
				return response.json();
			})
			.then(function(responseJson) {
				console.log('deleteZipFile 成功')
				// console.log(responseJson)
			})
		},

	},
  
	mounted() {
	},
}