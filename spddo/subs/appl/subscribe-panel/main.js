import tmpl from "./main.html!text"
import Vue from 'vue'


export default Vue.extend({
	template: tmpl,
	data(){
		return {
			active: [],
			unpaid: [],
			editing: null
		}
	},
	methods:{
		load(){
			this.control.active_subscriptions().
				then((result)=>{
					this.active = result;
				}).
				catch((err)=>{
					this.$root.error = err;
				})
			this.control.unpaid_subscriptions().
				then((result)=>{
					this.unpaid = result;
				}).
				catch((err)=>{
					this.$root.error = err;
				})
		},
		subscribe(){
			this.control.subscribe(this.editing.user_id,
								   this.editing.group_id,
								   this.editing.service_id).
				then((result)=>{
					this.editing = null;
				}).
				catch((err)=>{
					this.$root.error = err;
				});
		},
		cancel(){
			this.editing = null;
		},
		add(){
			this.editing = {
				user_id: null,
				group_id: null,
				service_id: null
			};
		}
	},
	events:{
		'subscription-added': function(item){
			this.unpaid.push(item);
			return true;
		},
		'subscription-active': function(item){
			this.active.push(item);
			var other = this.unpaid.find((o)=>{
				return o.id == item.id;
			});
			if(other){
				this.unpaid.splice(this.unpaid.indexOf(other),1);
			}
			return true;
		}
	}
});
