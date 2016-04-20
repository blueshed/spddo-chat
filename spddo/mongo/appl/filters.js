import Vue from 'vue'
import moment from 'moment'

Vue.filter('moment', function (value, format) {
	if(value){
		return moment(value).format(format || 'Do MMM YYYY')  
	}
})

function isFloat(n){
    return n != "" && !isNaN(n) && Math.round(n) != n;
}

Vue.filter('precision', function (value, precision) {
	if(value && isFloat(value)){
		return value.toPrecision(precision);  
	}
})
