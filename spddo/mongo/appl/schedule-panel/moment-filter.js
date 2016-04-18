import Vue from 'vue'

Vue.filter('moment', function (value, format) {
	if(value){
		return moment(value).format(format || 'Do MMM YYYY')  
	}
})
