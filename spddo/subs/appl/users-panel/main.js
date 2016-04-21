import tmpl from "./main.html!text"
import Vue from 'vue'


export default Vue.extend({
	template: tmpl,
	data(){
		return {
			users: null,
			editing_user: null,
			user_term: null
		}
	},
	methods:{
		filter_users(){
			this.control.filter_users(this.user_term).
				then((result)=>{
					this.users = result;
				}).
				catch((err)=>{
					this.$root.error = err;
				})
		},
		save_user(){
			this.control.save_user(this.editing_user.name,
								   this.editing_user.email,
								   this.editing_user.password,
								   this.editing_user.id).
				then((result)=>{
					this.editing_user = null;
				}).
				catch((err)=>{
					this.$root.error = err;
				});
		},
		cancel_user(){
			this.editing_user = null;
		},
		edit_user(item){
			this.editing_user = {
				id: item.id,
				name: item.name,
				email: item.email
			};
		},
		add_user(){
			this.editing_user = {
				id: null,
				name: null,
				email: null,
				password: null
			};
		}
	}
});
