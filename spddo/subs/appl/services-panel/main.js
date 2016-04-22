import tmpl from "./main.html!text"
import Vue from 'vue'


export default Vue.extend({
	template: tmpl,
	data(){
		return {
			services: null,
			editing_service: null,
			service_term: null
		}
	},
	methods:{
		filter_services(){
			this.control.filter_services(this.service_term).
				then((result)=>{
					this.services = result;
				}).
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
				name: null,
				description: null,
				cost: null,
				duration: null,
				token_url: null,
				cors: null
			};
		}
	}
});
