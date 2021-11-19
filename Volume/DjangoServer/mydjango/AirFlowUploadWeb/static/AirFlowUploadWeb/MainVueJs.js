// ############################################################
// ######################  通用function  ######################
// ############################################################

function _uuid(){
	// 計算隨機的UUID當作唯一Key
	var d = Date.now();
		if (typeof performance !== 'undefined' && typeof performance.now === 'function'){
			d += performance.now(); //use high-precision timer if available
		}
	return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
		var r = (d + Math.random() * 16) % 16 | 0;
		d = Math.floor(d / 16);
		return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
	});
}

function addz(num){
	// 小於10數值前方補0
	return num < 10 ? "0" + num : num
}

function compareNumbers(a, b) {
	return a - b;
}


// ############################################################
// ###################### 自訂義模組區塊 ######################
// ############################################################
// ▶▼
Vue.component("floder-tree-item", {
	template: `
	<div class='folderTreeItem'>
		<div>
			<label @click="toggle">{{folder_chosed}}{{item.ifOpen?'▼ ':'▶ '}}</label> 
			<label 
				class='folderLabel' 
				@click="$emit('click-folder', (item != undefined ? item : {}))"
				:style="folder_chosed==item.folderName?'background-color:#ff00ff;':''"
			>{{item.folderName}}</label>
		</div>
		<div class='childFolderDiv' v-show='item.ifOpen'>
			<floder-tree-item 
				v-for='(folderInfo, folderName, index) in item.folders'
				:item='folderInfo'
				:folder_chosed='folder_chosed'
				@click-folder="continueEmit"
			>
			</floder-tree-item>
		</div>
	</div>
	
	`,
	props: {
		item: Object,
		folder_chosed: String,
	},
	methods: {
		toggle: function() {
			this.item.ifOpen = !this.item.ifOpen;
		},
		
		continueEmit: function(D_fileList){
			console.log(this.folderChosed)
			if (D_fileList != undefined){
				this.$emit('click-folder', D_fileList)
			} else {
				this.$emit('click-folder', {})
			}
		},
	}
});


// ############################################################
// ######################  Vue App 區塊  ######################
// ############################################################

var VueSetting = new Vue({
	el: '#app',
	mixins: [
		VueSetting_dagEditer,
		VueSetting_dagListViewer, 
		VueSetting_dagInfoView
	],
	data: {
		// 基礎資訊
		massage: '030',
		version: 'v1.2149.0',

		loadingVue: false,

		airflowURL: "http://88.248.13.77:8890",

		show: true,
		NowPage: 'dagListViewer',
		
		WelcomeWord: '',

		DetailSheetChose: 'Runs_history',
		fileTreeInfo: {},
		fileTreeFolderChosed: '',
		DAGPausedSwitchWindowOpen: false,
		DAGPausedSwitchDAGID: null,
		DAGPausedSwitchPausedStatus: null,

		DAGTrigetRunWindowOpen: false,
		DAGTrigetRunDAGID: null,

		windmillList: [],
		// folderTreeInfo: {},
		// Misc.
		
		urlParas: {},
	},
  
	computed: {
		
	},
  
	methods: {
		clickHomeBtn(){
			this.closeDagDetailWindow()
		},

		clickDAGPauseStatusSwitch(dag_id, is_paused){
			console.log('點下DAG開關')
			console.log('dag_id: '+dag_id)
			this.DAGPausedSwitchDAGID = dag_id
			console.log('is_paused:'+is_paused)
			this.DAGPausedSwitchPausedStatus = is_paused
			this.DAGPausedSwitchWindowOpen = true
		},
		
		// 控制DAG ID的開關
		uploadDAGPauseStatus(dag_id, is_paused){
			let params = new FormData();
			params.append("DAG_ID", dag_id)
			params.append("is_paused", is_paused)

			fetch("/AirFlowUploadWeb/uploadDAGPauseStatus/", {
				method: 'POST',
				body: params
			})
			.then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				console.log('獲得DAG 開關狀態')
				console.log(myJson);
				VueSetting.DAGList[myJson['dag_id']]['is_paused'] = myJson['is_paused']
				VueSetting.DAGPausedSwitchWindowOpen = false
			});
		},

		getDAGDetailInfo(S_dagID){
			this.getDAGContent(S_dagID)
		},
		
		clickTrigerDAGRunButton(S_dagID){
			this.DAGTrigetRunWindowOpen = true
			this.DAGTrigetRunDAGID = S_dagID
		},
		
		trigerDAGByDAGID(S_dagID){
			var S_dagID_ = S_dagID
			fetch("/AirFlowUploadWeb/API/v1/TriggerNewDagRun/"+S_dagID_+"/", {
			})
			.then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				console.log(myJson)
				VueSetting.updateDAGRunsStatisticsInfoByDagID(S_dagID_)
				VueSetting.DAGTrigetRunWindowOpen = false
			});
		},
		
		UpdateFileTreeInfo(FileTreeInfo){
			console.log(FileTreeInfo)
			this.fileTreeInfo = FileTreeInfo
		},
		
		highlighter(code) {
		// js highlight example
			return Prism.highlight(code, Prism.languages.py, "py");
		},
		
		openFolderOnFileManagerTable(D_fileInfo){
			console.log(D_fileInfo)
			D_fileInfo.ifOpen = true
			this.fileTreeInfo = D_fileInfo
		},
		
		GetTaskInstances(D_runsInfo){
			console.log("=== GetTaskInstances ===")
			console.log(D_runsInfo.dag_run_id)
			console.log(D_runsInfo.dag_id)
			let params = new FormData();
			params.append("DAG_ID", D_runsInfo.dag_id)
			params.append("DAG_RUN_ID", D_runsInfo.dag_run_id)
			fetch("/AirFlowUploadWeb/GetTaskInstances/", {
				method: 'POST',
				body: params,
			}).then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				console.log(myJson)
				
				for (D_TaskInstanceChose of myJson['task_instances']){
					D_TaskInstanceChose['logChose'] = ''
				}
				Vue.set(
					D_runsInfo,
					'TaskInstances',
					myJson['task_instances']
				)
			})
		},
		
		GetgetTaskInstanceLog(TaskInstance, dag_run_id){
			if (TaskInstance['Logs'] == undefined){
				Vue.set(
					TaskInstance,
					'Logs',
					{}
				)
			}
			if (TaskInstance['Logs'][''+TaskInstance.logChose] == undefined){
				// console.log(TaskInstance)
				// console.log(dag_run_id)
				// console.log(TaskInstance.logChose)
				let params = new FormData();
				params.append("DAG_ID", TaskInstance.dag_id)
				params.append("DAG_RUN_ID", dag_run_id)
				params.append("TASK_ID", TaskInstance.task_id)
				params.append("LOG_INDEX", ''+TaskInstance.logChose)
				
				fetch("/AirFlowUploadWeb/GetTaskInstanceLog/", {
					method: 'POST',
					body: params,
				}).then(function(response) {
					return response.json();
				})
				.then(function(myJson) {
					console.log(myJson)
					Vue.set(
						TaskInstance['Logs'],
						''+TaskInstance.logChose,
						myJson['content']
					)
				})
				
			}
		},
		
		openDAGEditer(){
			this.NowPage = 'dagEditer'
		},
		
		openAddNewDAGEditer(){
			VueSetting.SetEditer({})
			VueSetting.openDAGEditer()
			VueSetting.GetTagsListFromServer()
			VueSetting.DAG_ID_locker = false
			VueSetting.lastPage = "dagListViewer"
		},

		updateUrlParas(){

			S_urlParastring = new URLSearchParams(this.urlParas).toString();
			// S_fullUrlPath = location.host + location.pathname + '?' + S_urlParastring
			S_fullUrlPath = "?" + S_urlParastring
			history.pushState(null,null,S_fullUrlPath)

			// location.search = new URLSearchParams(this.urlParas)
		},

		loadUrlParas(){
			var D_paras = {}
			let params = new URL(location.href).searchParams
			for (let pair of params.entries()) {
				D_paras[pair[0]] = pair[1]
			}
			this.urlParas = D_paras
			console.log(this.urlParas)
			this.actionByUrlParas()
		},

		actionByUrlParas(){
			if (this.urlParas['Page'] == 'dagListViewer'){

			}
			else if (this.urlParas['Page'] == 'dagEditer'){

			}
			else if (this.urlParas['Page'] == 'dagInfoView'){
				if (this.urlParas['dag_id'] != undefined){
					this.DAGInfoViewOpen(this.urlParas['dag_id'])
				}
			} else {
				// VueSetting.getDAGList()
				// VueSetting.getImportErrorList()
			}
		
		},
	},
  
})



function groupDAGrunsByStatus(L_dagList){
	for (D_dagChose of L_dagList){
		D_dagChose['dagRunsList']['groupBy'] = {}
		var L_dagRunsTotla = D_dagChose['dagRunsList']['dag_runs']
		for (D_dagRunChose of L_dagRunsTotla){
			var S_state = D_dagRunChose['state']
			if (D_dagChose['dagRunsList']['dag_runs'][S_state] == undefined){
				D_dagChose['dagRunsList']['dag_runs'][S_state] = []
			}
			D_dagChose['dagRunsList']['dag_runs'][S_state].push(D_dagRunChose)
			console.log(D_dagRunChose)
		}
	}
	return L_dagList
}



VueSetting.getDAGList().then(function(myJson) {VueSetting.loadUrlParas()})
VueSetting.getImportErrorList()
ShowLoadingWindow()

function getRandomArbitrary(min, max) {
	return Math.random() * (max - min) + min;
}

function ShowLoadingWindow() {
	VueSetting.loadingVue = true
	var L_windmillSettingList = []
	for (let windmillIndex of [...Array(30).keys()]) {
		let test = getRandomArbitrary(1,7)
		D_windmillSetting = {
			'index': windmillIndex,
			'left': getRandomArbitrary(5,90),
			'size': 160-(test*15),
			'bottom': 0+(test*60),
			'opacity': 1.1-test/10,
			'transition_delay':getRandomArbitrary(0,10)*0.5/10,
		}
		L_windmillSettingList.push(D_windmillSetting)
	}
	VueSetting.windmillList = L_windmillSettingList


	// VueSetting.WelcomeWord='Welcome To AirJob'
	setTimeout(function() {
		// Wrap every letter in a span
		var textWrapper = document.querySelector('.ml11 .letters');
		textWrapper.innerHTML = 'Welcome To AIRJOB'.replace(/([^\x00-\x80]|\w)/g, "<span class='letter'>$&</span>");
		anime.timeline({loop: false})
		.add({
			targets: '.ml11 .line',
			scaleY: [0,1],
			opacity: [0.5,1],
			easing: "easeOutExpo",
			duration: 700
		})
		.add({
			targets: '.ml11 .line',
			translateX: [0, document.querySelector('.ml11 .letters').getBoundingClientRect().width + 10],
			easing: "easeOutExpo",
			duration: 700,
			delay: 100
		})
		.add({
			targets: '.ml11 .letter',
			opacity: [0,1],
			easing: "easeOutExpo",
			duration: 100,
			offset: '-=775',
			delay: (el, i) => 34 * (i+1)
		})
		.add({
			targets: '.ml11',
			opacity: 0,
			duration: 1000,
			easing: "easeOutExpo",
			delay: 5000
		});
	}, 10);

	setTimeout(function() {
		VueSetting.loadingVue = false
	}, 2810);
}



// Wrap every letter in a span
try{
	var textWrapper = document.querySelector('.ml6 .letters');
	textWrapper.innerHTML = textWrapper.textContent.replace(/\S/g, "<span class='letter'>$&</span>");
	
	anime.timeline({loop: true})
	.add({
		targets: '.ml6 .letter',
		translateY: ["1.1em", 0],
		translateZ: 0,
		duration: 750,
		delay: (el, i) => 50 * i
	})
}
catch {}