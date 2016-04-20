//import 'bootstrap/css/bootstrap.min.css!'
import 'font-awesome/css/font-awesome.css!'
import './theme.css!'
import './main.css!'
import tmpl from "./main.html!text"

import Vue from 'vue'
import $ from 'jquery'
import bootstrap from 'bootstrap'

import LoginPanel from "./login-panel/main"
import ErrorPanel from "./error-panel/main"
import SchedulePanel from './schedule-panel/main'
import EventEditor from './event-editor/main'
import AssetEditor from './asset-editor/main'
import './filters'

Vue.config.debug = true;

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
			selected_event: null,
			selected_asset: null
		},
		components:{
			"login-panel": LoginPanel,
			"error-panel": ErrorPanel,
			'schedule-panel': SchedulePanel,
			'event-editor': EventEditor,
			'asset-editor': AssetEditor
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
			add_asset(){
				this.selected_event = null;
				this.$nextTick(()=>{
					this.selected_asset={
						title: 'untitled',
						type: 'area'
					}
				});
			}
		}
	});
	
});
