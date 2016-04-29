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
					this.$root.error = err.message;
				})
			this.control.unpaid_subscriptions().
				then((result)=>{
					this.unpaid = result;
				}).
				catch((err)=>{
					this.$root.error = err.message;
				})
		},
		subscribe(){
			this.control.subscribe(this.editing.user_id || null,
								   this.editing.group_id || null,
								   this.editing.service_id).
				then((result)=>{
					this.editing = null;
				}).
				catch((err)=>{
					this.$root.error = err.message;
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
		},
		set_user(value){
			this.editing.user_id = value.id
		},
		lookup_user(term, suggest){
			this.control.filter_users(term).
				then(suggest).
				catch((err)=>{
					this.$root.error = err.message;
				})
		},
		set_group(value){
			this.editing.group_id = value.id
		},
		lookup_group(term, suggest){
			this.control.filter_groups(term).
				then(suggest).
				catch((err)=>{
					this.$root.error = err.message;
				})
		},
		set_service(value){
			this.editing.service_id = value.id
		},
		lookup_service(term, suggest){
			this.control.filter_services(term).
				then(suggest).
				catch((err)=>{
					this.$root.error = err.message;
				})
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
