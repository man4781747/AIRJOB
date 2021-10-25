Object.prototype.getByKey = function (S_key, S_undefinedReturn) {
	return this[S_key]!=undefined?this[S_key]:S_undefinedReturn
}