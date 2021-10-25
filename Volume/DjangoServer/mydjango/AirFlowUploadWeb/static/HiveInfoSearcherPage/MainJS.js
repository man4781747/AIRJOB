var Vue_HiveSearcher = new Vue({
	el: '#hive-searcher',
	data: {
		massage: '030',
        tableInfoList : [],
        pageChose : 0,
        pageListChose : 0,
        pageMaxNum : 20,
        filterStr: '',
        filterStr_: '',
        sortBy: '',
        sortValue: 1,
	},
  
	computed: {
        pageList(){
            var pageListList = [[]]
            for (let pageIndex in this.tableData){
                let I_listInex = Math.floor(pageIndex/5)
                if (pageListList[I_listInex] == undefined){
                    pageListList[I_listInex] = []
                }
                pageListList[I_listInex].push(pageIndex)
            }

            if (this.pageListChose >=  pageListList.length){
                this.pageListChose = pageListList.length - 1
            }

            return pageListList
        },

		tableData(){
            if (this.sortBy != ""){
                afterSortList = []
                var sortByList = []
                for (let itemInfo of this.tableInfoList){
                    sortByList.push([itemInfo[this.sortBy],itemInfo])
                }

                sortByList.sort()
                if (this.sortValue == -1){
                    sortByList.reverse()
                }
                for (let itemInfo_after of sortByList){
                    afterSortList.push(itemInfo_after[1])
                }
            } else {
                afterSortList = this.tableInfoList
            }


            var afterFilterList = []
            if (this.filterStr.trim()==""){
                afterFilterList = afterSortList
            } else {
                for (let itemInfo of afterSortList){
                    for (key of Object.keys(itemInfo)){
                        if (itemInfo[key].indexOf(this.filterStr.trim())!= -1){
                            afterFilterList.push(itemInfo)
                            break
                        }
                    }
                }
            }
            var tableData = [[]]
            for (let itemIndex in afterFilterList){
                let I_page = Math.floor(itemIndex/this.pageMaxNum)
                if (tableData[I_page] == undefined){
                    tableData[I_page] = []
                }
                tableData[I_page].push(afterFilterList[itemIndex])
            }
            if (this.pageChose >=  tableData.length){
                this.pageChose = tableData.length - 1
            }
            return tableData
        },

	},
  
	methods: {
        runFilter(filterStr_){
            this.filterStr = filterStr_
        },

        updateTableInfoList(){
            this.pageChose = 0
            this.pageListChose = 0
            var newList = []

            for (testIndex in [...Array(532).keys()]){
                newList.push({
                    'tableName': 'TableName_' + testIndex,
                    'tableName_Chinese': '中文名稱_' + testIndex,
                    'DBNanme': 'DBNanme_' + testIndex,
                    'lastUpdate': 'lastUpdate_' + testIndex,
                    'status': (Math.random()>0.5)?'正常':'異常',
                    'updateFrequency': '頻率_' + testIndex,
                    'buildDate': '上架時間_' + testIndex,
                })
            }

            this.tableInfoList = newList
        },

        sortByBtmChose(sortByStr){
            if (this.sortBy == sortByStr){
                this.sortValue = this.sortValue * -1
            } else {
                this.sortValue = 1
            }
            this.sortBy = sortByStr
        },
	},

	mounted: function(){
        this.updateTableInfoList()
	},
})