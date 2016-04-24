import tmpl from "./main.html!text"
import Vue from 'vue'


export default Vue.extend({
	template: tmpl,
	data(){
		return {
			editing_service: null
		}
	},
	methods:{
		filter_services(term, suggest){
			this.control.filter_services(term).
				then(suggest).
				catch((err)=>{
					this.$root.error = err;
				})
		},
		save_service(){
			this.control.save_service(
					this.editing_service.name,
					this.editing_service.description,
					this.editing_service.cost,
					this.editing_service.duration,
					this.editing_service.token_url,
					this.editing_service.cors,
				   	this.editing_service.id).
				then((result)=>{
					this.editing_service = null;
				}).
				catch((err)=>{
					this.$root.error = err;
				});
		},
		cancel_service(){
			this.editing_service = null;
		},
		edit_service(item){
			this.$els.search_input.value = null;
			this.editing_service = {
				id: item.id,
				name: item.name,
				description: item.description,
				cost: item.cost,
				duration: item.duration,
				token_url: item.token_url,
				cors: item.cors
			};
		},
		add_service(){
			this.editing_service = {
				id: null,
				name: this.$els.search_input.value || null,
				description: null,
				cost: null,
				duration: null,
				token_url: null,
				cors: null
			};
			this.$els.search_input.value = null;
			this.$nextTick(()=>{
				this.$els.name_input.focus();
			});
		}
	}
});
