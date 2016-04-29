import tmpl from "./main.html!text"
import Vue from 'vue'

export default Vue.extend({
	template: tmpl,
	data(){
		return {
			editing_user: null
		}
	},
	methods:{
		filter_users(term, suggest){
			this.control.filter_users(term).
				then(suggest).
				catch((err)=>{
					this.$root.error = err.message;
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
					this.$root.error = err.message;
				});
		},
		cancel_user(){
			this.editing_user = null;
		},
		edit_user(item){
			this.$els.search_input.value = null;
			this.editing_user = {
				id: item.id,
				name: item.name,
				email: item.email
			};
		},
		remove_user(){
			
		},
		add_user(){
			this.editing_user = {
				id: null,
				name: this.$els.search_input.value || null,
				email: null,
				password: null
			};
			this.$els.search_input.value = null;
			this.$nextTick(()=>{
				this.$els.name_input.focus();
			});
		}
	}
});
