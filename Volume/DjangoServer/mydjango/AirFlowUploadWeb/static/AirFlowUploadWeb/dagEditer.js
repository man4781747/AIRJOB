var PythonOperator_Default_Index = 1
var BashOperator_Default_Index = 1
var RunPythonFile_Default_Index = 1
var nowDatetime = new Date()


// const prettyPrint = require('code-prettify');

// ############################################################
// ######################  通用function  ######################
// ############################################################

function getByKey(D_Object, S_key, S_undefinedReturn){
	return D_Object[S_key]!=undefined?D_Object[S_key]:S_undefinedReturn
}

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

// bash-operator-item 模組設定
Vue.component("bash-operator-item", {
    template:`
		<div :id="divId" class='dag-task-card'>
			<div class='dag-item-left-icon-background text-h-center' >
				<i class="fas fa-circle">
					<div class='task-type-word'>{{index}}</div>
				</i>
			</div>
			<div class="dag-item table-card">
				<div class="table-card-header color-lb" v-if="disable!=true" style='display:flex;'>
					<div class='flex-10'>
						<button 
							class="dag-toolbox-btn text-v-center text-h-center mouse-pointer" 
							@click="$emit('item-up', index)" 
							v-show="index != 1">
							<i class="fas fa-caret-up"></i>
						</button>
						<button class="dag-toolbox-btn text-v-center text-h-center mouse-pointer" @click="$emit('item-down', index)" v-show="index != max_index">
							<i class="fas fa-caret-down"></i>
						</button>
					</div>
					<div class='flex-80 text-v-center' style='color:#fff'>
						BashOperator
					</div>
					<div class='flex-10'>
						<button class="dag-toolbox-btn text-v-center text-h-center mouse-pointer" @click="$emit('delete-item', post.uuid)" style='float: right;'>
							<i class="fas fa-times"></i>
						</button>
						<button class="dag-toolbox-btn text-v-center text-h-center mouse-pointer" @click="post.ifOpen =! post.ifOpen" style='float: right;'>
							<i :class='post.ifOpen ? "fas fa-minus":"fas fa-plus"'></i>
						</button>

						
					</div>
				</div>
				<div class="table-card-body task-body" :style='post.ifOpen?"":"max-height: 0px;"'>
					<div  class="dag-item-label">
						<label class="input_area_label">流程 ID:</label>
						<input v-on:input="dag_code" v-model="post.tesk_id" placeholder="請輸入" :disabled="disable">
					</div>
					<div class="dag-item-label">
						<label class="input_area_label">.py檔案上傳:</label>
						<div class='task-py-code-input-area mouse-pointer'>
							<div class='task-py-code-input-area-input' @click="$refs[fileInputRef].click()">
								<div class='text-v-center'  style="width: -webkit-fill-available;">{{post.python_name}}</div>
								<i class="fas fa-file-alt btn avtive-btn"></i>
							</div>
							<div class='alert alert-warning' style='top: -.25rem;z-index: 0;' v-if='pyFileExists==true & NewFile==true'>
									<h5>
										<i class="fas fa-exclamation-triangle" style='margin:0px;'></i>
										Warning!!
									</h5>
									檔案已存在Server 要重複上傳?
									<div style='display: grid;'>
										<label 
											@click="$refs[UploadAnywayRef].click()"
											class='t-f-btn mouse-pointer'
										>{{uploaditem[uuid_key].UploadAnyway?'是':'否'}}
										</label>
										<input :ref='UploadAnywayRef' v-show='false' 
										type="checkbox" v-model='uploaditem[uuid_key].UploadAnyway'>
									</div>
							</div>
							<div class='alert alert-warning' style='top: -.25rem;z-index: 0;' v-else-if='pyFileExists==false & NewFile==false'>
									<h5>
										<i class="fas fa-exclamation-triangle" style='margin:0px;'></i>
										Warning!!
									</h5>
									Server上並無找到對應.py檔案，請重新上傳。
							</div>
							<div class='alert alert-success' style='top: -.25rem;z-index: 0;' v-else-if='pyFileExists==true & NewFile==false'>
									.py 存在，若要更新請重新上傳
							</div>
						</div>

						<input  
							:ref="fileInputRef"
							v-on:change="change_pyCodeFile($event.target.files[0])" 
							accept='.py'
							v-show='false'
							type="file"
						>
					</div>
					<div  class="dag-item-label" v-if='false'>
						<label class="input_area_label">parameters:</label>
						<input v-model="post.bash_command" placeholder="請輸入所需參數(若無則空)" :disabled="disable">
					</div>

				</div>
				<div class="table-card-footer" v-if='false'>
				</div>
			</div>
		</div>

    `,
	data: function(){
		return {
			detailOpen: false,
			pyFileExists: null,
			NewFile: false,
		}
	},
    props: ['post', 'disable', 'now_list', 'uuid_key', 'uploaditem', 'dag_id'],
    methods: {
        dag_code: function(){
			this.RemoveOtherWord()
            let return_string = this.post.tesk_id+` = BashOperator(
    task_id='`+this.post.tesk_id+`',
    bash_command='`+this.post.bash_command+`',
    dag=dag,
    trigger_rule=TriggerRule.ALL_DONE
    )
	
`
			Vue.set(this.post, "code", return_string)
		},

		RemoveOtherWord(){
			this.post.tesk_id = this.post.tesk_id.replaceAll(/\W/gm,'_')
		},

		change_pyCodeFile: function(file){
			// checkIfExistsTaskPyFile
			this.pyFileExists= null
			this.uploaditem[this.uuid_key]['file'] = file
			this.uploaditem[this.uuid_key]['status'] = 'Wait to upload'
			this.uploaditem[this.uuid_key]['debugFail'] = true
			this.uploaditem[this.uuid_key]['fileName'] = file.name
			this.post.python_name = file.name
			this.checkIfPyFileExists()
			this.NewFile = true
			// console.log(file)
		},

		checkIfPyFileExists: function(){
			if (this.post.python_name){
				var thisVueItem = this
				let form = new FormData();
				form.append('DAG_ID', this.dag_id)
				form.append('fileName', this.post.python_name)
				// console.log('準備檢查py檔案是否已存在')
				// console.log('DAG id: '+this.dag_id)
				// console.log('File name: '+this.post.python_name)
				fetch('/AirFlowUploadWeb/API/v1/'+VueSetting.projectName+'/checkIfExistsTaskPyFile/'+this.dag_id+'/', {
					method: 'POST',
					body: form,
				}).then(function(response) {
					return response.json();
				})
				.then(function(myJson) {
					// console.log(myJson);
					thisVueItem.pyFileExists = myJson['Exists']
				});
			}
		}

	},
	computed: {
		divId: function(){
			this.uploaditem[this.uuid_key]['dom_id'] = 'editer-input-task-card-'+this.uuid_key
			return 'editer-input-task-card-'+this.uuid_key
		},
		index: function(){
			return this.now_list.indexOf(this.uuid_key)+1
		},
		max_index: function(){
			return this.now_list.length
		},
		fileInputRef : function(){
			return "fileInput__"+this.uuid_key
		},

		UploadAnywayRef: function(){
			return "UploadAnyway__"+this.uuid_key
		},
	},
	created: function() { 
		this.dag_code()
		this.uploaditem[this.uuid_key]['VueCustomerItem'] = this
		this.uploaditem[this.uuid_key]['fileName'] = this.post.python_name
		this.checkIfPyFileExists()
	},
})


// ############################################################
// ######################  Vue App 區塊  ######################
// ############################################################

var VueSetting_dagEditer = {
	data: {
		DebugMode_Editer: false,
		dag_settingDaebugFail: true,

		lastPage: 'dagListViewer',
		DAG_ID_locker: true,
		dagUploadViewerOpen: false,
		dagSettingFileStatus: 'Wait',
		dagSettingFileStatusMessage: 'Wait',
		dagSettingFileStatusStyleClass: 'alert-warning',

		// 基礎資訊
		ForSetObject: true,
		DAGpyFileName : "",
		ownerValues : "",
		retries: 1,

		// dag id 相關
		dagIdValue: this.projectName,		
		dagIdCheckingState: 'Checking',
		dagIdCheckingStateCtyle: 'alert-warning',
		dagIdCheckPass: false,

		retry_delay: 5, 
		
		scheduleValues : "* * * * *",
		template_searchpath: "",
		dagDescriptionValue: "請輸入註解",
		code: "console.log('hello world')",
		uploadAnyway: false,
		ScheduleSettingTypeList_Date:['One time', 'Daily', 'Weekly', 'Monthly'],
		ScheduleSettingTypeChose_Date: 'One time',
		
		// tag視窗相關
		tagAdder: '',
		addTags : ['dasd','asdasd','adsgaregearth','rrrr','qwlihivzjshldivg'],
		serverTags : ['test1','test2','test3','test4','test5','test6'],
		tagFilter: '',
		serverTagsLoading: false,
		
		// cron 時間設定相關參數
		
		S_cronOnce: {
			'Date': new Date().format('yyyy-MM-dd'),
			'Time': new Date().format('hh:mm'),
		},
		
		// Date 設定相關
		I_DailyCronSetting: 1,
		L_WeeklyCronSetting: [0,1,2,3,4,5,6],
		D_MonthlyCronSetting: {
			'MonthlyList' : [...Array(13).keys()].slice(1),
			'DayList': [...Array(32).keys()].slice(1),
			'WeeklythList': [...Array(4).keys()],
			'WeekdayList': [...Array(7).keys()],
			'Type': '1'
		},
		D_cronDataSetting: {
			'Month': {
				cronType: '1',
				cronCollect: [],
				cron_Value: 1,
				maxValue: 12,
				windowShow: false,
				valueBias: 1,
				maxLength: 12,
			},
			'Day': {
				cronType: '1',
				cronCollect: [],
				cron_Value: 1,
				maxValue: 31,
				windowShow: false,
				valueBias: 1,
				maxLength: 31,
			},
			'Hour': {
				cronType: '1',
				cronCollect: [],
				cron_Value: 1,
				maxValue: 23,
				windowShow: false,
				valueBias: 0,
				maxLength: 24,
			},
			'Minute' : {
				cronType: '1',
				cronCollect: [],
				cron_Value: 1,
				maxValue: 59,
				windowShow: false,
				valueBias: 0,
				maxLength: 60,
			},
		},
		cronWeekDayCollect: [0,1,2,3,4,5,6],
		weekdayChinese: {
			'0' : '日',
			'1' : '一',
			'2' : '二',
			'3' : '三',
			'4' : '四',
			'5' : '五',
			'6' : '六',
			'7' : '日',
		},
		
		// Time 設定相關
		ScheduleSettingTypeList_Time: ['Specify', 'Loop'],
		ScheduleSettingTypeChose_Time: 'Specify',
		D_TimeSetting : {
			'Hour': {
				cronCollect: [0],
				cron_Value: 1,
			},
			'Minute' : {
				cronCollect: [0],
				cron_Value: 5,
			},
		},
		
		
		// task 視窗物件相關參數
		dag_item_build_list : {},  // 負責各DAG tasks 的詳細內容
		dag_item_build_index : [], // 負責各DAG tasks 的排列順序
		dag_item_wait_upload_list: {},

		// Misc.
		EmptyDAGSettingWindowClass: '', // 控制拉動放置檔案空間的style (之後可能會拿掉)
		uploadFileList: {},             // 上傳附件清單
		DAGpythonFileUploadStatue: "",  // 負責上傳狀態的顯示文字 (之後應該要移到 computed區塊比較正確)

		shake_upload_fail_window : true,

		// ### 已停用的參數，但可能日後會需要使用因此當做紀錄
		// dag_item_list: ["PythonOperator", "BashOperator", "RunPythonFile"], // 紀錄可以選的 DAG tasks物件 (已停用)
		// dag_item_chose : null,
		// start_date: nowDatetime.getFullYear() + "-" + addz(nowDatetime.getMonth()+1) + "-" + addz(nowDatetime.getDate()),
		// start_time: addz(nowDatetime.getHours()) + ":" + addz(nowDatetime.getMinutes()),
  },
  
	computed: {
		DAGStartDatetime(){
			if (this.ScheduleSettingTypeChose_Date == "One time"){
				return "datetime.strptime('"+this.S_cronOnce.Date +' '+this.S_cronOnce.Time+"','%Y-%m-%d %H:%M')"

			} 
			// return 'now() - timedelta(days=1)'
			return 'datetime.datetime(1990,1,1,0,0,0)'
		},
		
		DAGFileString(){
			let DAGFileString_return = `
import os
import shutil
import pendulum
from datetime import datetime, timedelta
import airflow
from airflow.utils import timezone
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.utils.trigger_rule import TriggerRule

now = timezone.utcnow
local_tz = pendulum.timezone('Asia/Taipei')

default_args = {
	'owner': "`+ this.ownerValues +`",
	'email': ['leekaiping@cathaylife.com.tw'],
	'email_on_failure': False,
	'email_on_retry': False,
	'depends_on_past': False,
	'start_date': (`+this.DAGStartDatetime+`).replace(tzinfo=local_tz),
	'retries': 1,
	'retry_delay': timedelta(hours=1),
}

dag = DAG(
	dag_id='`+this.dagIdValue+`', 
	description='''`+this.dagDescriptionValue+`''',
	default_args=default_args,
	schedule_interval='`+this.cronStringGet+`',
	catchup=False,
	template_searchpath=` + this.GetTemplateSearchpath + `,
	tags=['buildByDAGBuilder',`+this.getTagsStr+`],
)

START = DummyOperator(
	task_id='START',
	dag=dag
)

END = DummyOperator(
	task_id='END',
	dag=dag
)

`
			var taskIdList = ["START"];
			for (dagItemKey of this.dag_item_build_index){
				// console.log(dagItemKey)
				taskIdList.push(this.dag_item_build_list[dagItemKey]['tesk_id'])
				DAGFileString_return = DAGFileString_return + this.dag_item_build_list[dagItemKey]['code']
			}
			taskIdList.push('END')
			
			DAGFileString_return = DAGFileString_return + taskIdList.join(" >> ")
			DAGFileString_return = DAGFileString_return.trim()
			return DAGFileString_return
			
		},
		
		GetTemplateSearchpath(){
			if (this.template_searchpath.trim() == ''){
				return 'os.path.split(os.path.realpath(__file__))[0]'
			} else {
				return "'" + this.template_searchpath + "'"
			}
		},
		// GetNewData(){return this.dag_item_build_list},
		GetStartDateString(){
			let DateStringList = this.start_date.split('-')
			let TimeStringList = this.start_time.split(':')
			let timeList = []
			for (dateItemChose of DateStringList){
				timeList.push(parseInt(dateItemChose))
			}
			for (dateItemChose of TimeStringList) {
				timeList.push(parseInt(dateItemChose))
			}
			
			return timeList.join(',')
		},
	
		cornMonth (){
			if (this.D_cronDataSetting['Month'].cronType=='1'){
				if (this.D_cronDataSetting['Month'].cronCollect.length == 0){
					return '*'
				} else if (
					this.D_cronDataSetting['Month'].cronCollect.length == this.D_cronDataSetting['Month'].maxLength
				){
					return '*'
				}
				return this.D_cronDataSetting['Month'].cronCollect.sort(compareNumbers).join(',')
			} else {
				if (this.D_cronDataSetting['Month'].cron_Value==1){
					return "*"
				}
				return "*/"+this.D_cronDataSetting['Month'].cron_Value
			}
		},
		
		cornDay (){
			if (this.D_cronDataSetting['Day'].cronType=='1'){
				if (this.D_cronDataSetting['Day'].cronCollect.length == 0){
					return '*'
				} else if (
					this.D_cronDataSetting['Day'].cronCollect.length == this.D_cronDataSetting['Day'].maxLength
				){
					return '*'
				}
				return this.D_cronDataSetting['Day'].cronCollect.sort(compareNumbers).join(',')
			} else {
				if (this.D_cronDataSetting['Day'].cron_Value==1){
					return "*"
				}
				return "*/"+this.D_cronDataSetting['Day'].cron_Value
			}
		},
		
		cornHour (){
			if (this.D_cronDataSetting['Hour'].cronType=='1'){
				if (this.D_cronDataSetting['Hour'].cronCollect.length == 0){
					return '*'
				} else if (
					this.D_cronDataSetting['Hour'].cronCollect.length == this.D_cronDataSetting['Hour'].maxLength
				){
					return '*'
				}
				return this.D_cronDataSetting['Hour'].cronCollect.sort(compareNumbers).join(',')
			} else {
				if (this.D_cronDataSetting['Hour'].cron_Value==1){
					return "*"
				}
				return "*/"+this.D_cronDataSetting['Hour'].cron_Value
			}
		},
		
		cornMinute (){
			if (this.D_cronDataSetting['Minute'].cronType=='1'){
				if (this.D_cronDataSetting['Minute'].cronCollect.sort(compareNumbers).length == 0){
					return '*'
				} else if (
					this.D_cronDataSetting['Minute'].cronCollect.length == this.D_cronDataSetting['Minute'].maxLength
				){
					return '*'
				}
				return this.D_cronDataSetting['Minute'].cronCollect.join(',')
			} else {
				if (this.D_cronDataSetting['Minute'].cron_Value==1){
					return "*"
				}
				return "*/"+this.D_cronDataSetting['Minute'].cron_Value
			}
		},
		
		cornWeekday (){
			if (this.cronWeekDayCollect.length==0 | this.cronWeekDayCollect.length==7){
				return '*'
			}
			return this.cronWeekDayCollect.sort(compareNumbers).join(',').replace('0', '7')
		},
		
		cronWeekDayCollectSet() {
			if (this.cronWeekDayCollect.length==0){
				return new Set([1,2,3,4,5,6,7])
			}
			return new Set(this.cronWeekDayCollect)
		},
		
		cronTimeStr(){
			
		// D_TimeSetting : {
			// 'Hour': {
				// cronCollect: [0],
				// cron_Value: 1,
			// },
			// 'Minute' : {
				// cronCollect: [0],
				// cron_Value: 5,
			// },
		// },
			
			if (this.ScheduleSettingTypeChose_Time=='Specify'){
				return this.D_TimeSetting.Minute.cronCollect.slice(0).sort().join(',')+' '+this.D_TimeSetting.Hour.cronCollect.slice(0).sort().join(',')
			} else {
				return "*/"+this.D_TimeSetting.Minute.cron_Value+" *"
			}
		},
		
		cronStringGet(){
			if (this.ScheduleSettingTypeChose_Date == 'One time'){
				return '@once'
			}
			
			else if (this.ScheduleSettingTypeChose_Date == 'Daily'){
				return this.cronTimeStr + ' */'+ this.I_DailyCronSetting +' * *'
			}
			
			else if(this.ScheduleSettingTypeChose_Date == 'Weekly'){
				var cronList
				if (this.L_WeeklyCronSetting.length==0 | this.L_WeeklyCronSetting.length==7){
					cronList = '*'
				} else {
					cronList = this.L_WeeklyCronSetting.sort().join(',')
				}
				return this.cronTimeStr + ' * * ' + cronList
			}
			
			else if(this.ScheduleSettingTypeChose_Date == 'Monthly'){
				var dayStr
				var MonthStr
				var weekdayStr
			    MonthStr = this.D_MonthlyCronSetting['MonthlyList']
				if (MonthStr.length == 0 | MonthStr.length == 12){
					MonthStr = '*'
				} else {
					MonthStr = MonthStr.join(',')
				}
				
				dayList = this.D_MonthlyCronSetting['DayList']
				if (dayList.length == 0 | dayList.length == 31){
					dayStr = '*'
				} else {
					dayStr = dayList.join(',')
				}
				weekdayStr = '*'

				return this.cronTimeStr + ' '+dayStr+' '+MonthStr+' ' + weekdayStr
			}
			
			return 'N/A'
		},
		
		cronReadStringGet(){
			var cronReadString = ''
			if (this.ScheduleSettingTypeChose_Date == 'One time'){
				return '只會在 ' + this.S_cronOnce.Date +' '+this.S_cronOnce.Time + ' 執行一次'
			}
			else if (this.ScheduleSettingTypeChose_Date == 'Daily'){
				cronReadString = cronReadString + '每 ' + this.I_DailyCronSetting +  ' 天的'
			}
			
			else if(this.ScheduleSettingTypeChose_Date == 'Weekly'){
				var weekdayList = []
				if (this.L_WeeklyCronSetting.length==0 | this.L_WeeklyCronSetting.length==7){
					cronReadString = cronReadString + '每天的'
				} else {
					for (day of this.L_WeeklyCronSetting.sort()){
						weekdayList.push(this.weekdayChinese[''+day])
					}
					cronReadString = cronReadString + '在每個周' + weekdayList.join(',') +  '的'
				}
			}
			
			else if(this.ScheduleSettingTypeChose_Date == 'Monthly'){
				var monthList = this.D_MonthlyCronSetting['MonthlyList']
				var dayList = this.D_MonthlyCronSetting['DayList']
				if (
					(monthList.length == 0 | monthList.length == 12) & 
					(dayList.length == 0 | dayList.length == 31) 
				){
					cronReadString = cronReadString + '每天的'
				} else {
					if (monthList.length == 0 | monthList.length == 12){
						cronReadString = cronReadString + '每個月'
					} else {
						cronReadString = cronReadString + '在' + monthList.join(',') +'月中'
					}

					if (dayList.length == 0 | dayList.length == 31){
						cronReadString = cronReadString + '每一天的'
					} else {
						cronReadString = cronReadString + '的' + dayList.join(',') +'日的'
					}

				}
			}
			
			if (this.ScheduleSettingTypeChose_Time == 'Specify'){
				var TimeList = []
				for (hourChose of this.D_TimeSetting.Hour.cronCollect){
					for (minuteChose of this.D_TimeSetting.Minute.cronCollect){
						TimeList.push(addz(hourChose)+":"+addz(minuteChose))
					}
				}
				cronReadString = cronReadString + " "+ TimeList.join(', ') + " 時執行"
			} else if (this.ScheduleSettingTypeChose_Time == 'Loop'){
				cronReadString = cronReadString + "每隔" + this.D_TimeSetting.Minute.cron_Value +"分鐘執行"
			}


			return cronReadString
		},


		perViewCronDatetime(){
			var monthList = [...Array(13).keys()].slice(1)
			var dayList = [...Array(32).keys()].slice(1)
			var hourList = []
			var miunteList = []
			var cronWeekDayCollectSet = new Set([0,1,2,3,4,5,6])
			
			if (this.ScheduleSettingTypeChose_Date == 'Daily'){
				dayList = []
				for (let i=1;i<=31;i=i+parseInt(
					this.I_DailyCronSetting
				)){
					dayList.push(i)
				}
				// console.log(dayList)
			}
			
			else if(this.ScheduleSettingTypeChose_Date == 'Weekly'){
				cronWeekDayCollectSet = new Set(this.L_WeeklyCronSetting)
			}
			
			else if(this.ScheduleSettingTypeChose_Date == 'Monthly'){
				monthList = this.D_MonthlyCronSetting['MonthlyList'].sort(compareNumbers)
				
				if (this.D_MonthlyCronSetting['Type'] == '1'){
					dayList = this.D_MonthlyCronSetting['DayList'].sort(compareNumbers)
				} else if (this.D_MonthlyCronSetting['Type'] == '2') {
					dayList = []
					for (i of this.D_MonthlyCronSetting['WeeklythList'].sort(compareNumbers)){
						for (j of [...Array(8).keys()].slice(1)){
							dayList.push(i*7 + j)
						}
					}
					
					cronWeekDayCollectSet = new Set(this.D_MonthlyCronSetting.WeekdayList)
				}
			}
			
			else if(this.ScheduleSettingTypeChose_Date == 'Customer'){
				// 計算月份清單
				if (this.D_cronDataSetting['Month'].cronType=='2'){
					for (let i=1;i<=12;i=i+parseInt(
						this.D_cronDataSetting['Month'].cron_Value
					)){
						monthList.push(i)
					}
				} else {
					if (this.D_cronDataSetting['Month'].cronCollect.length == 0){
						var monthList = [...Array(13).keys()].slice(1)
					} else {
						var monthList = this.D_cronDataSetting['Month'].cronCollect
					}
				}
				// console.log('Month Chose: '+monthList)
				
				// 計算日期清單
				if (this.D_cronDataSetting['Day'].cronType=='2'){
					for (let i=1;i<=31;i=i+parseInt(
						this.D_cronDataSetting['Day'].cron_Value
					)){
						dayList.push(i)
					}
				} else {
					if (this.D_cronDataSetting['Day'].cronCollect.length == 0){
						var dayList = [...Array(32).keys()].slice(1)
					} else {
						var dayList = this.D_cronDataSetting['Day'].cronCollect
					}
				}
				// console.log('Day Chose: '+dayList)

				// 計算小時清單
				if (this.D_cronDataSetting['Hour'].cronType=='2'){
					for (let i=0;i<=23;i=i+parseInt(
						this.D_cronDataSetting['Hour'].cron_Value
					)){
						hourList.push(i)
					}
				} else {
					if (this.D_cronDataSetting['Hour'].cronCollect.length == 0){
						var hourList = [...Array(24).keys()]
					} else {
						var hourList = this.D_cronDataSetting['Hour'].cronCollect
					}
				}
				// console.log('Hour Chose: '+hourList)
				
				if (this.D_cronDataSetting['Minute'].cronType=='2'){
					for (let i=0;i<=59;i=i+parseInt(
						this.D_cronDataSetting['Minute'].cron_Value
					)){
						miunteList.push(i)
					}
				} else {
					if (this.D_cronDataSetting['Minute'].cronCollect.length == 0){
						var miunteList = [...Array(60).keys()]
					} else {
						var miunteList = this.D_cronDataSetting['Minute'].cronCollect
					}
				}
				// console.log('Minute Chose: '+miunteList)
				
				
				if (this.cronWeekDayCollect.length==0){
					cronWeekDayCollectSet =  new Set([1,2,3,4,5,6,7])
				} else {
					cronWeekDayCollectSet = new Set(this.cronWeekDayCollect)
				}
			}
	
			if (this.ScheduleSettingTypeChose_Time == 'Specify'){
				hourList = this.D_TimeSetting.Hour.cronCollect
				miunteList = this.D_TimeSetting.Minute.cronCollect
				
			} else if (this.ScheduleSettingTypeChose_Time == 'Loop'){
				hourList = [...Array(24).keys()]
				miunteList = []
				for (let i=0;i<=59;i=i+parseInt(
					this.D_TimeSetting.Minute.cron_Value
				)){
					miunteList.push(i)
				}
				
			}
	
			var dateItem
			var dataList = []
			var nowDatetime = new Date()
			var nowYear = nowDatetime.getFullYear()
			var nowTime = nowDatetime.getTime()
			
			var cronWeekDayCollectList = Array.from(cronWeekDayCollectSet)
			
			// date 與 day 同時都有指定
			if (cronWeekDayCollectList.length!=7 & dayList.length != 31){
				// console.log('date 與 day 同時都有指定')
				for (let yearChose of [nowYear, nowYear+1, nowYear+2, nowYear+3, nowYear+4]){
					for (let monthChose of monthList){
						for (let dayChose of [...Array(32).keys()].slice(1)){
							dateItem = new Date()
							dateItem.setYear(yearChose)
							dateItem.setDate(dayChose)
							dateItem.setMonth(monthChose-1)
							// 去除比現在時間還舊的項目
							// 去除setDay後 month 被 +1 的項目
							// 去除同時都不在 dayList 以及 cronWeekDayCollectList 的項目
							if (
								(dateItem.getTime() < nowTime) | 
								(dateItem.getMonth() != monthChose-1) | 
								(cronWeekDayCollectList.indexOf(dateItem.getDay()) == -1 & dayList.indexOf(dateItem.getDate()) == -1)
							){continue}
							for (let hourChose of hourList){
								for (let miunteChose of miunteList){
									dateItem.setHours(hourChose)
									dateItem.setMinutes(miunteChose)
									if (dateItem.getTime() >= nowTime){
										dataList.push(dateItem.format("(w) yyyy-MM-dd hh:mm"))
										console.log(dateItem.format("(w) yyyy-MM-dd hh:mm"))
									}
									if (dataList.length >= 11){break}
								}
								if (dataList.length >= 11){break}
							}
							if (dataList.length >= 11){break}
						}
						if (dataList.length >= 11){break}
					}
					if (dataList.length >= 11){break}
				}
				return dataList
			} 
			// date 與 day 非同時指定
			else {
				for (let yearChose of [nowYear, nowYear+1, nowYear+2, nowYear+3, nowYear+4]){
					for (let monthChose of monthList){
						for (let dayChose of dayList){
							dateItem = new Date()
							dateItem.setYear(yearChose)
							dateItem.setDate(dayChose)
							dateItem.setMonth(monthChose-1)
							if (
								(dateItem.getTime() < nowTime) | (dateItem.getMonth() != monthChose-1)
							){continue}
							for (let hourChose of hourList){
								for (let miunteChose of miunteList){
									dateItem.setHours(hourChose)
									dateItem.setMinutes(miunteChose)
									if (
										dateItem.getTime() >= nowTime & cronWeekDayCollectSet.has(dateItem.getDay())
									){
										dataList.push(dateItem.format("(w) yyyy-MM-dd hh:mm"))
										// console.log(dateItem.format("(w) yyyy-MM-dd hh:mm"))
									}
									if (dataList.length >= 11){break}
								}
								if (dataList.length >= 11){break}
							}
							if (dataList.length >= 11){break}
						}
						if (dataList.length >= 11){break}
					}
					if (dataList.length >= 11){break}
				}
				return dataList
			}
		},
		
		uploadFiles(){
			return Object.keys(this.uploadFileList)
		},
  
		getTagsStr(){
			let tagArray = Array.from(new Set(this.addTags.slice(0)))
			if (tagArray.length != 0){
				return "'"+tagArray.join("','")+"'"
			}
			return ""
		},

		uploadButtomAllow(){
			var checkList = []
			if (this.dagIdValue == ""){
				checkList.push({
					'dom_id': 'editer-input-dag-id',
					'failMessage' : "排程ID不得為空。"
				})
			}
			else if (this.dagIdValue == this.projectName + "_"){
				checkList.push({
					'dom_id': 'editer-input-dag-id',
					'failMessage' : "請輸入排程ID。"
				})
			}
			else if (this.dagIdCheckPass==false){
				checkList.push({
					'dom_id': 'editer-input-dag-id',
					'failMessage' : "排程ID重複，請換成一個新的"
				})
			}

			if (this.ownerValues==""){
				checkList.push({
					'dom_id': 'editer-input-owner',
					'failMessage' : "Owner不得為空"
				})
			}

			if (Object.keys(this.dag_item_wait_upload_list).length == 0){
				checkList.push({
					'dom_id': 'editer-input-tasks',
					'failMessage' : "請建立至少一項流程"
				})
			} 

			var taskIdSet = new Set()
			for (taskUuid of Object.keys(this.dag_item_wait_upload_list)){
				// console.log(this.dag_item_build_list[taskUuid].python_name)
				if (!(this.dag_item_build_list[taskUuid].python_name)){
					checkList.push({
						'dom_id': this.dag_item_wait_upload_list[taskUuid]['dom_id'],
						'failMessage' : "流程ID: "+this.dag_item_build_list[taskUuid].tesk_id+ "沒有上傳檔案"
					})	
				}

				if (this.dag_item_build_list[taskUuid].tesk_id.trim()==""){
					checkList.push({
						'dom_id': this.dag_item_wait_upload_list[taskUuid]['dom_id'],
						'failMessage' : "流程ID不得為空"
					})	
				} else if (taskIdSet.has(this.dag_item_build_list[taskUuid].tesk_id)){
					checkList.push({
						'dom_id': this.dag_item_wait_upload_list[taskUuid]['dom_id'],
						'failMessage' : "流程ID: "+this.dag_item_build_list[taskUuid].tesk_id+ "發現重複的ID，請更換"
					})	
				}
				taskIdSet.add(this.dag_item_build_list[taskUuid].tesk_id)
			}
			return checkList	
		},

		allUploadStatus(){
			let L_successList = []
			let L_failList = []
			let L_uploadingList = []

			for (S_key of Object.keys(this.dag_item_wait_upload_list)){
				let fileItem = this.dag_item_wait_upload_list[S_key]
				if (
					!(fileItem.VueCustomerItem.pyFileExists & !fileItem.UploadAnyway) & fileItem.file != null
				) {
					if (fileItem['uploadStatus'] == 'Success'){
						L_successList.push(S_key)
					} else if (fileItem['uploadStatus'] == 'Fail'){
						L_failList.push(S_key)
					} else {
						L_uploadingList.push(S_key)
					}
				}
			}

			for (S_key of Object.keys(this.uploadFileList)){
				let fileItem = this.uploadFileList[S_key]
				if (
					!(fileItem.Exists & !fileItem.IfUploadAnyway)
				) {
					if (fileItem['uploadStatus'] == 'Success'){
						L_successList.push(S_key)
					} else if (fileItem['uploadStatus'] == 'Fail'){
						L_failList.push(S_key)
					} else {
						L_uploadingList.push(S_key)
					}
				}
			}
			
			if (
				L_successList.length == 0 &
				L_failList.length == 0 &
				L_uploadingList.length == 0
			) {
				return 'Success'
			}

			if (L_uploadingList.length != 0){
				return 'Wait'
			} else {
				if (L_successList.length == 0){
					return 'Fail'
				} else if (L_failList.length == 0){
					return 'Success'
				} else {
					return 'Uploading'
				}
			}
		},
  },
  
	methods: {

		dagIDChange: function(){
			this.RemoveOtherWord('dagIdValue')
			if (this.dagIdValue.indexOf(this.projectName+"_")!=0){
				this.dagIdValue = this.projectName + "_" + this.dagIdValue
			}
			if (this.DAG_ID_locker == false){
				this.checkDAGIDExists()
			}
			this.checkAllAttachFilesExists()
			this.checkAllTaskPyFileExists()
		},

		checkDAGIDExists(){
			if (this.DAG_ID_locker){
				return null
			}

			if (this.dagIdValue == this.projectName + "_"){
				VueSetting.dagIdCheckingState = 'Empty'
				VueSetting.dagIdCheckingStateCtyle = 'alert-danger'
				VueSetting.dagIdCheckPass = false
				return null
			}

			this.dagIdCheckingState = 'Checking'
			this.dagIdCheckingStateCtyle = 'alert-warning'
			this.dagIdCheckPass = false

			fetch('/AirFlowUploadWeb/GetAllDAGIDList/', {
			}).then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				// console.log(myJson['dag_list']);
				if (myJson['dag_list'].indexOf(VueSetting.dagIdValue)!=-1){
					VueSetting.dagIdCheckingState = 'Fail'
					VueSetting.dagIdCheckingStateCtyle = 'alert-danger'
					VueSetting.dagIdCheckPass = false
				} else {
					VueSetting.dagIdCheckingState = 'OK'
					VueSetting.dagIdCheckingStateCtyle = 'alert-success'
					VueSetting.dagIdCheckPass = true
				}
			});


		},

		BuildNewDAGItem: function(S_itemName, S_tesk_id, S_python_name="", S_bash_command, uuidInput=null) {
			// console.log(S_itemName)
			if (S_itemName == "BashOperator"){
				if (uuidInput==null){
					var uuid = _uuid()
				} else {
					var uuid = uuidInput
				}
				if (S_tesk_id == null){
					S_tesk_id = "BashOperator_Default_"+BashOperator_Default_Index
				}
				
				
				Vue.set(
					this.dag_item_build_list,
					uuid,
					{
						uuid: uuid,
						type: "BashOperator",
						tesk_id: S_tesk_id,
						python_name: S_python_name,
						bash_command : S_bash_command,
						ifOpen: true,
					}
				)
				this.dag_item_build_index.push(uuid)
				Vue.set(
					this.dag_item_wait_upload_list,
					uuid,
					{
						'file': null,
						'uploadStatus': 'Wait',
						'uploadMessage': 'Waiting for the DAG file to be created successfully',
						'uploadStatusStyleClass': 'alert-warning',
						'UploadAnyway': false,
						'VueCustomerItem': null,

					}
				)

				BashOperator_Default_Index += 1
			}
		},
		
		item_up : function(index){
			let TempData = this.dag_item_build_index[index-2]
			Vue.set(this.dag_item_build_index, index-2, this.dag_item_build_index[index-1])
			Vue.set(this.dag_item_build_index, index-1, TempData)
		},
		
		item_down: function(index){
			let TempData = this.dag_item_build_index[index]
			Vue.set(this.dag_item_build_index, index, this.dag_item_build_index[index-1])
			Vue.set(this.dag_item_build_index, index-1, TempData)
		},
		
		DelDAGItemByUuid(S_uuid){
			// console.log("del : "+S_uuid)
			Vue.delete(
				this.dag_item_build_list,
				S_uuid
			)

			Vue.delete(
				this.dag_item_wait_upload_list,
				S_uuid
			)

			let index = this.dag_item_build_index.indexOf(S_uuid);
			if (index > -1) {
				  this.dag_item_build_index.splice(index, 1);
				}
		},
		
		UpdateDAGFileString(D_uuid){
			// console.log(D_uuid)
		},
		
		switchCronType(S_witchCron){
			if (this.D_cronDataSetting[S_witchCron].cronType == '1'){
				this.D_cronDataSetting[S_witchCron].cronType = '2'
			} else {
				this.D_cronDataSetting[S_witchCron].cronType = '1'
			}
		},
		
		switchCronChangeWindow(S_cronType){
			// console.log(this.D_cronDataSetting[S_cronType].windowShow)
			this.D_cronDataSetting[S_cronType].windowShow = !this.D_cronDataSetting[S_cronType].windowShow
		},
		
		GetDAGsettingCSV(file){
			// console.log(file);
			if (this.dag_item_build_index.length != 0){
				var ifDelAllDAGStages = confirm('要清空現有的 Stages 嗎?');
				if (ifDelAllDAGStages) {
					this.clearAllDAGStaegs()
				} else {
				}
			}
			
			
			let reader = new FileReader();
			reader.onload = function () {
				let L_csvData = this.result.split(/[\r\n]+/g)
				for (csvLineItem of L_csvData.slice(1)){
					if (csvLineItem){
						L_lineData = csvLineItem.split(/[\t\r,]+/g)
						VueSetting.BuildNewDAGItem('BashOperator', L_lineData[0], L_lineData[1])
					}
				}
			};
			reader.readAsText(file);
		},
		
		clearAllDAGStaegs(){
			while (this.dag_item_build_index.length != 0){
				this.DelDAGItemByUuid(this.dag_item_build_index[0])
			}
		},
		
		addAttachFiles(files){
			test = files
			// console.log(files)
			for (let fileChose of files){
				Vue.set(
					VueSetting.uploadFileList,
					fileChose.name + fileChose.size + fileChose.type,
					{
						'status': 'Wait To Load',
						'content' : "",
						'fileBlob' : fileChose,
						'styleSet' : 'background-color: #a7aeae;',
						'IfUploadAnyway': false,
						'Exists': false,
						'uploadStatus': 'Wait',
						'uploadMessage': 'Waiting for the DAG file to be created successfully',
						'uploadStatusStyleClass': 'alert-warning',
						'debugFail': true,
					}
				)
			}
			
			var fileIndex = 0
			function readFile(fileIndexInput) {
				if (fileIndexInput >=  files.length){
					return null
				}
				var file = files[fileIndexInput]
				var S_fileKey = file.name + file.size + file.type
				var reader = new FileReader();  
				reader.onload = function (e) {
					let S_content = this.result
					VueSetting.uploadFileList[S_fileKey]['content'] = S_content
					VueSetting.uploadFileList[S_fileKey]['status'] = "Load Done! Wait for upload to server."
					VueSetting.checkAttachFileExists(VueSetting.uploadFileList[S_fileKey])
					readFile(fileIndexInput+1)
				}
				VueSetting.uploadFileList[S_fileKey]['status'] = "Loading..."
				reader.readAsText(file);			
			}
			readFile(fileIndex)
		},
		
		delUploadFile(S_md5){
			Vue.delete(this.uploadFileList, S_md5)
		},
		
		uploadNewDAGSettingInfoToServer(){
			this.dagSettingFileStatus = 'Uploading'
			this.dagSettingFileStatusMessage = 'Uploading...'
			this.dagSettingFileStatusStyleClass = 'alert-warning'


			var SettingInfo = new FormData();
			if ((this.DebugMode_Editer & this.dag_settingDaebugFail) == false){
				SettingInfo.append('DAG_ID', this.dagIdValue)
				SettingInfo.append('Owner', this.ownerValues)
				SettingInfo.append('Retries', this.retries)
				SettingInfo.append('Retry_delay', this.retry_delay)
				SettingInfo.append('ScheduleDateType', this.ScheduleSettingTypeChose_Date)
				SettingInfo.append('ScheduleTimeType', this.ScheduleSettingTypeChose_Time)
				SettingInfo.append('ScheduleString', this.cronReadStringGet)
				SettingInfo.append('CronString', this.cronStringGet)
			} else {
				// console.log('DebugMode: 強制失敗')
			}

			var ScheduleSettingInfo = {}
			if (this.ScheduleSettingTypeChose_Date == 'One time') {
				// SettingInfo.append('ScheduleSettingInfo')
				ScheduleSettingInfo = {
					'Date': this.S_cronOnce['Date'],
					'Time': this.S_cronOnce['Time'],
				}
			} 
			else if (['Daily', 'Weekly', 'Monthly'].indexOf(this.ScheduleSettingTypeChose_Date) != -1){
				if (this.ScheduleSettingTypeChose_Date == 'Daily') {
					ScheduleSettingInfo['DailyValue'] = this.I_DailyCronSetting
					// this.I_DailyCronSetting = getByKey(D_SettingData, 'DailyValue', 1)
				}
				else if (this.ScheduleSettingTypeChose_Date == 'Weekly') {
					ScheduleSettingInfo['WeeklyValue'] = this.L_WeeklyCronSetting
					// this.L_WeeklyCronSetting =  getByKey(D_SettingData, 'WeeklyValue', [0,1,2,3,4,5,6])
				}
				else if (this.ScheduleSettingTypeChose_Date == 'Monthly') {
					ScheduleSettingInfo['MonthlyValue'] = {
						'MonthlyList': this.D_MonthlyCronSetting['MonthlyList'],
						'DayList'    : this.D_MonthlyCronSetting['DayList'],
					}
					// let D_MonthlyCronSetting_Get = getByKey(D_SettingData, 'MonthlyValue', {})
					
					// this.D_MonthlyCronSetting = {
						// 'MonthlyList' : getByKey(D_MonthlyCronSetting_Get, 'MonthlyList',[...Array(13).keys()].slice(1)),
						// 'DayList' : getByKey(D_MonthlyCronSetting_Get, 'DayList',[...Array(32).keys()].slice(1)),
					// }
				}
				ScheduleSettingInfo['TimeSetting'] = {
					'Hour': {},
					'Minute': {},
				}
				if (this.ScheduleSettingTypeChose_Time == 'Specify'){
					ScheduleSettingInfo['TimeSetting']['Hour']['cronCollect'] = this.D_TimeSetting['Hour']['cronCollect']
					ScheduleSettingInfo['TimeSetting']['Minute']['cronCollect'] = this.D_TimeSetting['Minute']['cronCollect']
				}
				else if (this.ScheduleSettingTypeChose_Time == 'Loop'){
					ScheduleSettingInfo['TimeSetting']['Hour']['cron_Value'] = this.D_TimeSetting['Hour']['cron_Value']
					ScheduleSettingInfo['TimeSetting']['Minute']['cron_Value'] = this.D_TimeSetting['Minute']['cron_Value']
				}
			}
			
			SettingInfo.append('ScheduleSettingInfo_String', JSON.stringify(ScheduleSettingInfo))
			
			SettingInfo.append('Tags_JSONString', JSON.stringify(this.addTags))
			SettingInfo.append('Description', this.dagDescriptionValue)
			
			
			SettingInfo.append('TaskSettingList_JSONString', JSON.stringify(this.dag_item_build_list))
			SettingInfo.append('TaskSettingIndex_JSONString', JSON.stringify(this.dag_item_build_index))
			// dag_item_build_list : {},  // 負責各DAG tasks 的詳細內容
			// dag_item_build_index : [], // 負責各DAG tasks 的排列順序
			
			
			uploadFetch = fetch('/AirFlowUploadWeb/API/v1/'+this.projectName+'/uploadNewDAGSettingInfo/', {
				method: 'POST',
				body: SettingInfo,
			}).then(function(response) {
				// console.log('uploadNewDAGSettingInfoToServer 得到回應')
				return response.json();
			})
			.then(function(myJson) {
				// console.log(myJson);
				if (myJson['result'] == 'Success'){
					VueSetting.dagSettingFileStatus = 'Success'
					VueSetting.dagSettingFileStatusMessage = 'Upload successfully!'
					VueSetting.dagSettingFileStatusStyleClass = 'alert-success'

				} else if (myJson['result'] == 'Fail'){
					VueSetting.dagSettingFileStatus = 'Fail'
					VueSetting.dagSettingFileStatusMessage = myJson['message']
					VueSetting.dagSettingFileStatusStyleClass = 'alert-danger'
				}
				return myJson
			});
			
			return uploadFetch
		},
		// 負責上傳所有Task用的py檔案至Server
		uploadAllTaskPyFilesToServer(){
			for (let S_fileKey in this.dag_item_wait_upload_list){
				if (this.dag_item_wait_upload_list[S_fileKey] != null &
				this.dag_item_wait_upload_list[S_fileKey]['status'] == 'Wait to upload'){
					this.uploadTaskPyFilesToServer(this.dag_item_wait_upload_list[S_fileKey])
				}
			}
		},

		// 負責上傳單個有Task用的py檔案至Server
		uploadTaskPyFilesToServer(D_fileInfo){
			if (D_fileInfo['UploadAnyway']==false & D_fileInfo['VueCustomerItem'].pyFileExists){
				// console.log('已存在 不重新上傳')
				return null
			}
			var D_fileInfo = D_fileInfo
			// console.log('準備上傳Task用Py檔案')
			// console.log('DAG ID : '+ this.dagIdValue)
			// console.log('檔案名稱: '+ D_fileInfo['file'].name)
			// console.log('檔案資訊: ', D_fileInfo['file'])

			D_fileInfo['uploadStatus'] = 'Uploading'
			D_fileInfo['uploadMessage'] = 'Uploading...'
			D_fileInfo['uploadStatusStyleClass'] = 'alert-warning'


			var form = new FormData();
			if (!(this.DebugMode_Editer & D_fileInfo['debugFail'])){
				form.append("fileName", D_fileInfo['file'].name)
			} else {
				// console.log('DebugMode: 強制失敗')
			}
			form.append("DAG_ID", this.dagIdValue)
			form.append("fileUploaded", D_fileInfo['file'])
			form.append("UploadAnyway", D_fileInfo['UploadAnyway'])

			fetch('/AirFlowUploadWeb/API/v1/'+this.projectName+'/uploadTaskPyFile/'+this.dagIdValue+'/', {
				method: 'POST',
				body: form,
			}).then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				// console.log(myJson);
				if (myJson['result'] == 'Success') {
					D_fileInfo['uploadStatus'] = myJson['result']
					D_fileInfo['uploadMessage'] = myJson['message']
					D_fileInfo['uploadStatusStyleClass'] = 'alert-success'
				}
				else if (myJson['result'] == 'Fail'){
					D_fileInfo['uploadStatus'] = myJson['result']
					D_fileInfo['uploadMessage'] = myJson['message']
					D_fileInfo['uploadStatusStyleClass'] = 'alert-danger'
				}

			});

		},

		// 負責上傳所有附件檔案至Server
		uploadAllAttachFilesToServer(uploadAnyway=null){
			for (let S_fileKey in this.uploadFileList){
				this.uploadAttachFileToServer(S_fileKey, uploadAnyway)
			}
		},
		
		// 負責上傳單個附件檔案至Server
		uploadAttachFileToServer(S_fileKey, uploadAnyway=null){
			// console.log('準備上傳附件檔案')
			// console.log('DAG ID : '+ this.dagIdValue)
			// console.log('檔案名稱: '+ this.uploadFileList[S_fileKey]['fileBlob'].name)
			// console.log('檔案資訊: ', this.uploadFileList[S_fileKey]['fileBlob'])
			// console.log('強制上傳與否: '+ uploadAnyway)
			if (
				this.uploadFileList[S_fileKey]['uploadStatus'] != 'Success'
			){
				this.uploadFileList[S_fileKey]['uploadStatus'] = 'Uploading'
				this.uploadFileList[S_fileKey]['uploadMessage'] = 'Uploading...'
				this.uploadFileList[S_fileKey]['uploadStatusStyleClass'] = 'alert-warning'


				let form = new FormData();
				if (!(this.DebugMode_Editer & this.uploadFileList[S_fileKey]['debugFail'])){
					form.append("DAG_ID", this.dagIdValue)
				} else {
					// console.log('DebugMode: 強制失敗')
				}
				form.append("fileUploaded", this.uploadFileList[S_fileKey]['fileBlob'])
				form.append("fileName", this.uploadFileList[S_fileKey]['fileBlob'].name)
				form.append("fileKey", S_fileKey)

				fetch('/AirFlowUploadWeb/API/v1/'+this.projectName+'/UploadAttachFile/'+this.dagIdValue+'/', {
					method: 'POST',
					body: form,
				}).then(function(response) {
					return response.json();
				})
				.then(function(myJson) {
					// console.log(myJson);
					VueSetting.uploadFileList[myJson['fileKey']]['status'] = myJson['Result']
					if (myJson['Result'] == 'Success'){
						VueSetting.uploadFileList[myJson['fileKey']]['uploadStatus'] = 'Success'
						VueSetting.uploadFileList[myJson['fileKey']]['uploadMessage'] = 'Upload successfully'
						VueSetting.uploadFileList[myJson['fileKey']]['uploadStatusStyleClass'] = 'alert-success'
					} else {
						VueSetting.uploadFileList[myJson['fileKey']]['uploadStatus'] = 'Fail'
						VueSetting.uploadFileList[myJson['fileKey']]['uploadMessage'] = myJson['message']
						VueSetting.uploadFileList[myJson['fileKey']]['uploadStatusStyleClass'] = 'alert-danger'
					}
				});
				this.uploadFileList[S_fileKey]['status'] = 'Upload To Server ING...'
				this.uploadFileList[S_fileKey]['styleSet'] = 'background-color: #ffe699;'
			}
		},
		
		uploadDAGFileToServer(uploadAnyway=null){
			let emptyList = this.checkInputIfEmpty()
			if (emptyList.length != 0){
				alert('以下欄位不能為空白: '+emptyList.join(', '))
				return null
			}
			
			
			let DAGpyFileform = new FormData();
			DAGpyFileform.append("DAGpyFileName", this.DAGpyFileName+'.py')
			DAGpyFileform.append("DAGpyFileContent", this.DAGFileString)
			DAGpyFileform.append("DAG_ID", this.dagIdValue)
			// console.log(uploadAnyway)
			if (uploadAnyway==null){
				DAGpyFileform.append("UploadAnyway", this.uploadAnyway)
			} else {
				DAGpyFileform.append("UploadAnyway", uploadAnyway)
			}
			
			fetch('/AirFlowUploadWeb/UploadDAGPythonFile/', {
				method: 'POST',
				body: DAGpyFileform,
			}).then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				// console.log(myJson);
				if (myJson['Result'] == 'IfUploadAnyway'){
					let IfUploadAnyway = confirm("DAG ID已存在，是否覆蓋?")
					if (IfUploadAnyway == true){
						VueSetting.uploadDAGFileToServer(IfUploadAnyway)
					} else {
						VueSetting.DAGpythonFileUploadStatue = VueSetting.DAGpyFileName +"已存在，不覆蓋"
					}
				} else {
					if (myJson['Result'] == 'success'){
						VueSetting.DAGpythonFileUploadStatue = VueSetting.DAGpyFileName +" 上傳完畢"
						VueSetting.uploadFilesToServer()
					} else {
						VueSetting.DAGpythonFileUploadStatue = VueSetting.DAGpyFileName +" 上傳失敗，失敗原因: "+myJson['Result']
					}
				}
			});
			this.DAGpythonFileUploadStatue = this.DAGpyFileName +" 上傳中"
		},
		
		checkInputIfEmpty(){
			let L_empty = []
			if (this.dagIdValue == ''){
				L_empty.push('DAG ID')
			}
			
			return L_empty
		},
	
		checkAllAttachFilesExists(){
			for (fileNameKey of Object.keys(this.uploadFileList)){
				this.checkAttachFileExists(this.uploadFileList[fileNameKey])
			}
		},

		checkAttachFileExists(D_attachItem){
			var D_attachItem = D_attachItem
			// console.log('準備檢查attach檔案是否已存在')
			// console.log('DAG id: '+this.dagIdValue)
			// console.log('File name: '+D_attachItem.fileBlob.name)
			let form = new FormData();
			form.append('DAG_ID', this.dagIdValue)
			form.append('fileName', D_attachItem.fileBlob.name)

			fetch('/AirFlowUploadWeb/API/v1/'+this.projectName+'/checkIfExistsAttachFile/'+this.dagIdValue+'/', {
				method: 'POST',
				body: form,
			}).then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				// console.log(myJson);
				D_attachItem['Exists'] = myJson['Exists']
			});
		},

		checkAllTaskPyFileExists(){
			for (let S_uuid of Object.keys(this.dag_item_wait_upload_list)){
				this.dag_item_wait_upload_list[S_uuid].VueCustomerItem.checkIfPyFileExists()
			}
		},

		allSwitchButtonClick(S_type){
			if (this.D_cronDataSetting[S_type].cronCollect.length != this.D_cronDataSetting[S_type].maxValue + 1 - this.D_cronDataSetting[S_type].valueBias){
				this.D_cronDataSetting[S_type].cronCollect = [...Array(this.D_cronDataSetting[S_type].maxValue+1).keys()].slice(
					this.D_cronDataSetting[S_type].valueBias
				)
			} else {
				this.D_cronDataSetting[S_type].cronCollect = []
			}
		},
		
		highlighter(code) {
		// js highlight example
			return Prism.highlight(code, Prism.languages.python, "py");
		},
	  
		GetRemoveOtherWord(S_strTypeName){
			return S_strTypeName.replaceAll(/\W/gm,'_')
		},

		RemoveOtherWord(S_strTypeName){
			this[S_strTypeName] = this[S_strTypeName].replaceAll(/\W/gm,'_')
		},
		
		AddTag(S_tag){
			if (S_tag == null){
				S_tag = this.tagAdder
			}
			if (S_tag.trim() == ""){
				return null
			}
			if (this.addTags.indexOf(S_tag) == -1){
				this.addTags.push(S_tag)
				this.tagAdder = ''
			}
		},
		
		RemoveTag(S_tag){
			this.addTags = this.addTags.filter(function(item) {
				return item !== S_tag
			});
		},
		
		GetTagsListFromServer(){
			// /AirFlowUploadWeb/GetDAGs_buildByDAGTags/
			this.serverTagsLoading = true
			fetch("/AirFlowUploadWeb/API/v1/"+this.projectName+"/GetDAGs_buildByDAGTags/")
			.then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				// console.log(myJson['TagList']);
				VueSetting.serverTags = myJson['TagList']
				VueSetting.serverTagsLoading = false
			});
			
		},
		
		GetDAGIDListFromServer(){
			// /AirFlowUploadWeb/GetDAGs_buildByDAGTags/
			this.serverTagsLoading = true
			fetch("/AirFlowUploadWeb/GetExistDAGIDList/")
			.then(function(response) {
				return response.json();
			})
			.then(function(myJson) {
				// console.log(myJson);
				VueSetting.serverTags = myJson['TagList']
				VueSetting.serverTagsLoading = false
			});
		},
		
		SetEditer(D_SettingData){
			
			// DAGpyFileName : "",
			this.dag_settingDaebugFail = true

			this.dagUploadViewerOpen = false
			this.dagSettingFileStatus = 'Wait'
			this.dagSettingFileStatusMessage = 'Wait'
			this.dagSettingFileStatusStyleClass = 'alert-warning'

			// 基礎資訊

			this.ownerValues = getByKey(D_SettingData,'Owner', '')
			this.retries = getByKey(D_SettingData,'Retries', 1)
			this.retry_delay = getByKey(D_SettingData,'Retry_delay', 0)
			this.dagDescriptionValue = getByKey(D_SettingData,'Description', '請輸入註解')
			
			// dag id 相關
			this.dagIdValue = getByKey(D_SettingData,'DAG_ID', '')		

			// tag視窗相關
			this.addTags = getByKey(D_SettingData, 'Tags', [])
			
			//// cron 時間設定基礎數值
			// Once
			this.S_cronOnce = {
				'Date': new Date().format('yyyy-MM-dd'),
				'Time': new Date().format('hh:mm'),
			}
			
			// Date 設定相關
			this.I_DailyCronSetting= 1,
			this.L_WeeklyCronSetting= [0,1,2,3,4,5,6],
			this.D_MonthlyCronSetting= {
				'MonthlyList' : [...Array(13).keys()].slice(1),
				'DayList': [...Array(32).keys()].slice(1),
				'WeeklythList': [...Array(4).keys()],
				'WeekdayList': [...Array(7).keys()],
				'Type': '1'
			},
			
			// Time 設定相關
			this.ScheduleSettingTypeChose_Time = 'Specify',
			this.D_TimeSetting = {
				'Hour': {
					cronCollect: [0],
					cron_Value: 1,
				},
				'Minute' : {
					cronCollect: [0],
					cron_Value: 5,
				},
			},
			
			// cron 時間設定相關參數
			this.ScheduleSettingTypeChose_Date = getByKey(D_SettingData, 'ScheduleDateType', 'One time')
			this.ScheduleSettingTypeChose_Time = getByKey(D_SettingData, 'ScheduleTimeType', 'Specify')
			//// 依照不同狀態設定對應數值
			if (this.ScheduleSettingTypeChose_Date == 'One time') {
				let D_ScheduleSettingInfo = getByKey(D_SettingData, 'ScheduleSettingInfo', {})
				this.S_cronOnce = {
					'Date': getByKey(
								D_ScheduleSettingInfo,
								'Date',
								new Date().format('yyyy-MM-dd')
							),
					'Time': getByKey(
								D_ScheduleSettingInfo,
								'Time',
								new Date().format('hh:mm')
							),
				}
			} else if (['Daily', 'Weekly', 'Monthly'].indexOf(this.ScheduleSettingTypeChose_Date) != -1){
				let D_ScheduleSettingInfo = getByKey(D_SettingData, 'ScheduleSettingInfo', {})
				// console.log(D_ScheduleSettingInfo)
				if (this.ScheduleSettingTypeChose_Date == 'Daily') {
					this.I_DailyCronSetting = getByKey(D_ScheduleSettingInfo, 'DailyValue', 1)
				}
				else if (this.ScheduleSettingTypeChose_Date == 'Weekly') {
					this.L_WeeklyCronSetting =  getByKey(D_ScheduleSettingInfo, 'WeeklyValue', [0,1,2,3,4,5,6])
				}
				else if (this.ScheduleSettingTypeChose_Date == 'Monthly') {
					let D_MonthlyCronSetting_Get = getByKey(D_ScheduleSettingInfo, 'MonthlyValue', {})
					
					this.D_MonthlyCronSetting = {
						'MonthlyList' : getByKey(D_MonthlyCronSetting_Get, 'MonthlyList',[...Array(13).keys()].slice(1)),
						'DayList' : getByKey(D_MonthlyCronSetting_Get, 'DayList',[...Array(32).keys()].slice(1)),
					}
				}
				
				this.ScheduleSettingTypeChose_Time =  getByKey(D_SettingData, 'ScheduleTimeType', 'Specify')
				
				let D_TimeSetting = getByKey(D_ScheduleSettingInfo, 'TimeSetting', {})
				// console.log(D_TimeSetting)
				if (this.ScheduleSettingTypeChose_Time == 'Specify'){
					let HourSettingGet = getByKey(D_TimeSetting, 'Hour', {})
					// console.log(getByKey(HourSettingGet, 'cronCollect', [0]))
					this.D_TimeSetting['Hour']['cronCollect'] = getByKey(HourSettingGet, 'cronCollect', [0])
					
					let MinuteSettingGet = getByKey(D_TimeSetting, 'Minute', {})
					// console.log(getByKey(MinuteSettingGet, 'cronCollect', [0]))
					this.D_TimeSetting['Minute']['cronCollect'] = getByKey(MinuteSettingGet, 'cronCollect', [0])
				}
				else if (this.ScheduleSettingTypeChose_Time == 'Loop'){
					let HourSettingGet = getByKey(D_TimeSetting, 'Hour', {})
					this.D_TimeSetting['Hour']['cron_Value'] = getByKey(HourSettingGet, 'cron_Value', [0])
					
					let MinuteSettingGet = getByKey(D_TimeSetting, 'Minute', {})
					this.D_TimeSetting['Minute']['cron_Value'] = getByKey(MinuteSettingGet, 'cron_Value', [0])
				}
			}
			
			
			// task 視窗物件相關參數
			// dag_item_build_list : {},  // 負責各DAG tasks 的詳細內容
			this.dag_item_build_list = {}
			this.dag_item_wait_upload_list = {}

			// console.log("test:", getByKey(D_SettingData, 'TaskSettingList', {}))
			var D_TaskSettingList = getByKey(D_SettingData, 'TaskSettingList', {})
			for (uuid_key of Object.keys(D_TaskSettingList)) {
				this.BuildNewDAGItem(
					D_TaskSettingList[uuid_key]['type'],
					D_TaskSettingList[uuid_key]['tesk_id'],
					D_TaskSettingList[uuid_key]['python_name'],
					D_TaskSettingList[uuid_key]['bash_command'],
					D_TaskSettingList[uuid_key]['uuid'],
				)
			}

			// dag_item_build_index : [], // 負責各DAG tasks 的排列順序
			this.dag_item_build_index = getByKey(D_SettingData, 'TaskSettingIndex', [])

			// Misc.
			this.uploadFileList = {}            // 上傳附件清單
		},
		
		UploadButtomClick(){
			if (this.uploadButtomAllow.length!=0){
				this.shake_upload_fail_window = false
				setTimeout(function() {
					VueSetting.shake_upload_fail_window = true
				}, 0);
				return null
			}
			this.dagUploadViewerOpen = true
			this.uploadNewDAGSettingInfoToServer().then(function(myJson) {
				if (myJson['result'] == 'Success'){
					// uploadNewDAGSettingInfoToServer 成功後才會上傳其餘檔案
					VueSetting.uploadAllTaskPyFilesToServer()
					VueSetting.uploadAllAttachFilesToServer()

				} else if (myJson['result'] == 'Fail'){
					// console.log('Oops!')
				}
				return myJson
			});

		},

		retryUploadNewDAGSettingInfoToServer(){
			this.uploadNewDAGSettingInfoToServer().then(function(myJson) {
				if (myJson['result'] == 'Success'){
					// uploadNewDAGSettingInfoToServer 成功後才會上傳其餘檔案
					VueSetting.uploadAllTaskPyFilesToServer()
					VueSetting.uploadAllAttachFilesToServer()

				} else if (myJson['result'] == 'Fail'){
					// console.log('Oops!')
				}
				return myJson
			});
		},

		retryUploadFilesToServer(){
			VueSetting.uploadAllTaskPyFilesToServer()
			VueSetting.uploadAllAttachFilesToServer()
		},

		scrollToDOMID(S_DOMID){
			document.getElementById(S_DOMID).scrollIntoView(true)
			document.scrollingElement.scrollTop = document.scrollingElement.scrollTop - 20
		},

		backToLastPage(){
			this.dagUploadViewerOpen  = false
			this.SetEditer({})
			this.NowPage = this.lastPage
			if (this.lastPage == "dagInfoView"){
				this.UpdateAllSheetInfo()
			} else if (this.lastPage == "dagListViewer"){
				this.getDAGList()
			}
		},
	},
  
	mounted() {
		this.GetTagsListFromServer()

		this.$refs.select_frame.ondragleave = (e) => {
		  e.preventDefault();  //阻止離開時的瀏覽器預設行為
		  VueSetting.EmptyDAGSettingWindowClass = ''
		//   console.log('拉離開了')
		},
		
		this.$refs.select_frame.ondrop = (e) => {
			VueSetting.EmptyDAGSettingWindowClass = ''
			e.preventDefault();    //阻止拖放後的瀏覽器預設行為
			const data = e.dataTransfer.files;  // 獲取檔案物件
			if (data.length < 1) {
			return;  // 檢測是否有檔案拖拽到頁面     
			}
			// console.log(e.dataTransfer.files);
			const formData = new FormData();
			for (let i = 0; i < e.dataTransfer.files.length; i++) {
			// console.log(e.dataTransfer.files[i]);
			if (e.dataTransfer.files[i].name.indexOf('csv') === -1) {
			  alert('只允許上傳.csv檔案');
			  return;
			}
			formData.append('uploadfile', e.dataTransfer.files[i], e.dataTransfer.files[i].name);
			}
			// console.log(e.dataTransfer.files[0]);
			VueSetting.GetDAGsettingCSV(e.dataTransfer.files[0])
		};
			
		this.$refs.select_frame.ondragenter = (e) => {
		e.preventDefault();  //阻止拖入時的瀏覽器預設行為
		// console.log('拉進來了')
		VueSetting.EmptyDAGSettingWindowClass = 'AliceblueWindow'
		};
			
		this.$refs.select_frame.ondragover = (e) => {
		e.preventDefault();    //阻止拖來拖去的瀏覽器預設行為
		};
		
		this.$refs.select_uploadFileArea.ondragleave = (e) => {
		  e.preventDefault();  //阻止離開時的瀏覽器預設行為
		  VueSetting.EmptyDAGSettingWindowClass = ''
		//   console.log('拉離開了')
		},
		
		this.$refs.select_uploadFileArea.ondrop = (e) => {
			VueSetting.EmptyDAGSettingWindowClass = ''
			e.preventDefault();    //阻止拖放後的瀏覽器預設行為
			const data = e.dataTransfer.files;  // 獲取檔案物件
			if (data.length < 1) {
				return;  // 檢測是否有檔案拖拽到頁面     
			}
			VueSetting.inputTest(data)
		};
			
		this.$refs.select_uploadFileArea.ondragenter = (e) => {
		e.preventDefault();  //阻止拖入時的瀏覽器預設行為
		// console.log('拉進來了')
		VueSetting.EmptyDAGSettingWindowClass = 'AliceblueWindow'
		};
		
		this.$refs.select_uploadFileArea.ondragover = (e) => {
		e.preventDefault();    //阻止拖來拖去的瀏覽器預設行為
		};
	},
	
	uploadAllDAGRunsInfo(){
		for (S_dagID of Object.keys(this.DAGList)){
			this.uploadDAGRunsInfoByDagId(S_dagID)
		}
	},
}


// VueSetting.GetTagsListFromServer()
// ############################################################
// ################ JS output出檔案相關function ###############
// ############################################################

function clickDownload(aLink){
	// 輸出 DAG.py 檔案(已停用)
	str =  encodeURIComponent(VueSetting.DAGFileString.replace(/(^\s*)|(\s*$)/g, ""));
	aLink.download = VueSetting.DAGpyFileName
	aLink.href = "data:text/csv;charset=utf-8,"+str;
}

function OutputDAGStagesSettingCSV(aLink){
	// 輸出 DAGStagesSetting.cav 檔案
	if (VueSetting.dag_item_build_index.length == 0){
		return null
	}
	var outputDAGStagesSettingCSVString = "Task ID,Bash Command\n"
	for (dagItemKey of VueSetting.dag_item_build_index){
		outputDAGStagesSettingCSVString += VueSetting.dag_item_build_list[dagItemKey]['tesk_id']
		outputDAGStagesSettingCSVString += ','
		outputDAGStagesSettingCSVString += VueSetting.dag_item_build_list[dagItemKey]['bash_command']+'\n'
	}
	// console.log(outputDAGStagesSettingCSVString)
	var data = outputDAGStagesSettingCSVString;
	var blob = new Blob([data], {
		type : "application/octet-stream"
	});
	aLink.href = URL.createObjectURL(blob);
}

