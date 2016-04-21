import tmpl from "./main.html!text"
import Vue from 'vue'


export default Vue.extend({
	template: tmpl,
	data(){
		return {
			editing: null,
			unpaid: []
		}
	},
	methods:{
		load(){
			this.control.unpaid_subscriptions(
						this.editing.user_id, 
						this.editing.group_id).
				then((result)=>{
					this.unpaid = result;
				}).
				catch((err)=>{
					this.$root.error = err;
				})
		},
		pay(){
			this.control.make_payment(this.editing.user_id,
								   	  this.editing.group_id).
				then((result)=>{
					this.editing = null;
					this.unpaid = [];
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
				group_id: null
			};
		}
	}
});
