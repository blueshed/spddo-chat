import './main.css!'
import tmpl from "./main.html!text"

import Vue from 'vue'

Vue.config.debug = true;

import UsersPanel from './users-panel/main'
import GroupsPanel from './groups-panel/main'
import ServicesPanel from './services-panel/main'
import SubscribePanel from './subscribe-panel/main'
import PaymentPanel from './payment-panel/main'


System.import('/api.js').then(({Control})=>{

	Control.prototype.install = function(Vue){
		Vue.prototype.control = this;
	};

	Vue.use(new Control());

	new Vue({
		el: ".main",
		template: tmpl,
		data:{
			status: null,
			error: null,
			user: null,
			users: null,
			editing_user: null,
			user_term: null
		},
		components:{
			'users-panel': UsersPanel,
			'groups-panel': GroupsPanel,
			'services-panel': ServicesPanel,
			'subscribe-panel': SubscribePanel,
			'payment-panel': PaymentPanel
		},
		created(){
			this.user = this.control.user;
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
		},
		methods:{
			
		}
	});
	
});
