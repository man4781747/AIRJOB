var VueSetting_dagListViewer = {
	data: {
		ImportErrorList: [],
		DAGList: {},
		uploadingDAGListWindow: false,
		listFilterString: '',
	},
  
	computed: {
		projectName(){
			projectName = location.pathname.match(
				/\/AirFlowUploadWeb\/testHTML\/(\S*)\//
			)[1]
			return projectName
		},
		test(){
			this.filterChanged()
			return this.listFilterString
		},
	},
  
	methods: {
		getDAGList() {
			// 獲得DAG清單
			if (this.uploadingDAGListWindow == true){
				return null
			}
			this.uploadingDAGListWindow = true
			var fetchReult = fetch("/AirFlowUploadWeb/API/v1/"+this.projectName+"/GetExistDAGIDList/")
			.then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				// console.log('獲得DAG清單')
				// console.log(myJson);
				
				// L_dagList = groupDAGrunsByStatus(myJson['DAG_List'])
				VueSetting.DAGList = myJson
				for (S_dagID of Object.keys(myJson)){
					myJson[S_dagID]['filterShow'] = true
				}


				VueSetting.uploadingDAGListWindow = false
				VueSetting.uploadAllRunsInfo()
				return myJson;
			});
			return fetchReult
		},
		
		getImportErrorList(){
			fetch("/AirFlowUploadWeb/GetImportErrorList/").then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				// console.log(myJson)
				for (ErrorInfo of myJson['import_errors']){
					ErrorInfo['show'] = false
				}
				
				
				Vue.set(
					VueSetting,
					'ImportErrorList',
					myJson['import_errors']
				)
			})
		},

		uploadAllRunsInfo(){
			for (S_dagIDChose of Object.keys(this.DAGList)){
				this.updateDAGRunsStatisticsInfoByDagID(S_dagIDChose)
			}
		},
		
		updateDAGRunsStatisticsInfoByDagID(S_dagID){
			let params = new FormData();
			var S_dagID = S_dagID
			if (this.DAGList[S_dagID]['updateRunsStatistics'] == true){
				return null
			}
			Vue.set(
				this.DAGList[S_dagID],
				'updateRunsStatistics',
				true
			)
			params.append("DAG_ID", S_dagID)
			fetch("/AirFlowUploadWeb/GetDAGRunsStatistics/", {
				method: 'POST',
				body: params
			}).then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				// console.log(myJson)
				Vue.set(
					VueSetting.DAGList[S_dagID],
					'updateRunsStatistics',
					false
				)
				Vue.set(
					VueSetting.DAGList[S_dagID],
					'RunsStatistics',
					myJson['DAG_runs_statistics']
				)
				Vue.set(
					VueSetting.DAGList[S_dagID],
					'LastRun',
					myJson['LastRun']
				)
				
				if (VueSetting.NowPage=="dagListViewer" &
					VueSetting.DAGList[S_dagID].is_paused == false &
					new Set(['queued','scheduled','running']).has(myJson['LastRun'].Result.state)
				){
					setTimeout(function() {
						console.log('持續更新Last Run : '+S_dagID)
						VueSetting.updateDAGRunsStatisticsInfoByDagID(S_dagID)
					}, 2000);
				}


			})
		},

		DAGInfoViewOpen(dag_id){
			this.urlParas = {
				'Page': "dagInfoView",
				'dag_id': dag_id,
			}
			this.updateUrlParas()
			this.DAGDetailOpen = dag_id
			this.loadExistDAGSettingInfo(dag_id)
			this.getDAGContent(dag_id)
			this.uploadDAGRunsInfoByDagId(dag_id)
			this.getFileManagerInfoByDAGId(dag_id)
			this.closeDagLogWindow()
			this.NowPage="dagInfoView"
		},

		updateDAGPauseStatus(dag_id){
			let params = new FormData();
			params.append("DAG_ID", dag_id)

			fetch("/AirFlowUploadWeb/GetDAGPauseStatus/", {
				method: 'POST',
				body: params
			})
			.then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				console.log('獲得DAG 開關狀態')
				console.log(myJson);
				VueSetting.DAGList[myJson['DAG_ID']]['is_paused'] = myJson['is_paused']
			});
		},

		filterChanged(){
			L_filterStringList = this.listFilterString.split(',')
			for (S_dagID of Object.keys(this.DAGList)){
				this.DAGList[S_dagID]['filterShow'] = true
			}

			for (S_filterString of L_filterStringList){
				for (S_dagID of Object.keys(this.DAGList)){
					if (this.DAGList[S_dagID]['filterShow'] == false){
						continue
					}

					this.DAGList[S_dagID]['filterShow'] = false
					if (S_filterString == ""){
						this.DAGList[S_dagID]['filterShow'] = true
						continue
					}
					if (S_dagID.indexOf(S_filterString) != -1){
						this.DAGList[S_dagID]['filterShow'] = true
						continue
					}
					if (S_dagID.indexOf(S_filterString) != -1){
						this.DAGList[S_dagID]['filterShow'] = true
						continue
					}
					if (this.DAGList[S_dagID].Owner.indexOf(S_filterString) != -1){
						this.DAGList[S_dagID]['filterShow'] = true
						continue
					}
					for (tagChose of this.DAGList[S_dagID].tags){
						if (tagChose.name.indexOf(S_filterString) != -1){
							this.DAGList[S_dagID]['filterShow'] = true
							break
						}
					}
				}
			}
		},

		filterAdd(S_string){
			L_filterStringList_ = this.listFilterString.split(',')
			L_filterStringList = []
			L_filterStringList_.forEach(item => {
				if (item!='') {
					L_filterStringList.push(item)
				}
			  })
			if (L_filterStringList.indexOf(S_string) == -1){
				L_filterStringList.push(S_string)
			}
			this.listFilterString = L_filterStringList.join()
			this.filterChanged()
		},
	},
  
	mounted() {
	},
}