import tmpl from "./main.html!text"
import Vue from 'vue'


export default Vue.extend({
	template: tmpl,
	data(){
		return {
			editing_group: null
		}
	},
	methods:{
		filter_groups(term, suggest){
			this.control.filter_groups(term).
				then(suggest).
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
			this.$els.search_input.value = null;
			this.editing_group = {
				id: item.id,
				name: item.name
			};
		},
		add_group(){
			this.editing_group = {
				id: null,
				name: this.$els.search_input.value || null
			};
			this.$els.search_input.value = null;
			this.$nextTick(()=>{
				this.$els.name_input.focus();
			});
		}
	}
});
