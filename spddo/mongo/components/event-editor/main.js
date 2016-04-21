import tmpl from "./main.html!text"
import './main.css!'
import Vue from 'vue'

export default Vue.extend({
	props:['selected'],
	template: tmpl,
	data(){
		return {
			saving: false,
			selection: {
				id: null,
				title: null,
				from_date: null,
				to_date: null,
				asset_id: null,
			}
		}
	},
	computed:{
		can_allocated(){
			return this.selection.title;
		}
	},
	created(){
		this.edit(this.selected);
	},
	methods:{
		uid() {
		    function _p8(s){
		        var p = (Math.random().toString(16)+"000000000").substr(2,8);
		        return s ? "-" + p.substr(0,4) + "-" + p.substr(4,4) : p ;
		    }
		    return _p8() + _p8(true);
		},
		allocate(){
			this.saving=true;
			var id = this.selection.id || this.uid();
			this.control.allocate({
					id: id,
					title: this.selection.title,
					from_date: this.selection.start.unix(),
					to_date: this.selection.end.unix(),
					asset_id: this.selection.resource_id
				}).
				then((result)=>{
					this.selection.id = id;
					this.saved();
				}).
				catch((err)=>{
					this.saving=false;
					this.$root.error = err;
				});
		},
		unallocate(){
			this.control.unallocate(this.selection.id).
				then((result)=>{
					this.clear_selection();
				}).
				catch((err)=>{
					this.$root.error = err;
				});
		},
		saved(){
			setTimeout(()=>{
				this.saving = false;
			},500);
		},
		clear_selection(){
			this.selected = null;
		},
        set_selection(values){
        	Object.keys(values).map((key)=>{
        		this.$set("selection."+key,values[key]);
        	});
        },
        edit(value){
			this.set_selection(value || {
				id: null,
				title: null,
				start: null,
				end: null,
				resource_id: null,
				resource: null
			});
        }
	},
	watch:{
		selected(value){
			this.edit(value);
		}
	}
});