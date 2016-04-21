import tmpl from "./main.html!text"
import Vue from 'vue'


export default Vue.extend({
	template: tmpl,
	data(){
		return {
			groups: null,
			editing_group: null,
			group_term: null
		}
	},
	methods:{
		filter_groups(){
			this.control.filter_groups(this.group_term).
				then((result)=>{
					this.groups = result;
				}).
				catch((err)=>{
					this.$root.error = err;
				})
		},
		save_group(){
			this.control.save_group(this.editing_group.name,
								   this.editing_group.id).
				then((result)=>{
					this.editing_group = null;
				}).
				catch((err)=>{
					this.$root.error = err;
				});
		},
		cancel_group(){
			this.editing_group = null;
		},
		edit_group(item){
			this.editing_group = {
				id: item.id,
				name: item.name
			};
		},
		add_group(){
			this.editing_group = {
				id: null,
				name: null
			};
		}
	}
});
