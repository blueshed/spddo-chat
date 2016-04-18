import 'bootstrap/css/bootstrap.min.css!'
import 'font-awesome/css/font-awesome.css!'
import './main.css!'

import Vue from 'vue'
import $ from 'jquery'
import bootstrap from 'bootstrap'

import SchedulePanel from './schedule-panel/main'

Vue.config.debug = true;

System.import('/api.js').then(({Control})=>{

	Control.prototype.install = function(Vue){
		Vue.prototype.control = this;
	};

	Vue.use(new Control());

	new Vue({
		el: ".container",
		data:{
			status: null,
			error: null,
			user: null
		},
		components:{
			'schedule-panel': SchedulePanel
		},
		created(){
			this.control.init((signal, message)=>{
					this.$dispatch(signal, message);
					this.$broadcast(signal, message);
				}).
			then((status)=>{
				this.status = status;
			}).
			catch((err)=>{
				this.error = err;
			});
		}
	});
	
});
