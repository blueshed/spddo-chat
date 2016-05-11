import tmpl from "./main.html!text"
import './main.less!'
import Vue from 'vue'
import MapPanel from 'components/map-panel/main'

export default Vue.extend({
	props: ['selected'],
	template: tmpl,
	data(){
		return {
			saving: false,
			selection: {
				id: null,
				title: null,
				location:{
					lat: null,
					lng: null,
					zoom: null,
				},
				group_id: null,
				group: null,
				type: null
			}
		}
	},
	computed:{
		can_save(){
			return this.selection.title && this.selection.type;
		}
	},
	components:{
		'map-panel': MapPanel
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
		save(){
			this.saving = true;
			var id = this.selection.id || this.uid();
			this.control.save_asset({
					id: id,
					name: this.selection.title,
					location: this.selection.location,
					type: this.selection.type,
					group_id: this.selection.group_id || null
				}).
				then((result)=>{
					this.selection.id = id;
					this.saved();
				}).
				catch((err)=>{
					this.saving = false;
					this.$root.error = err.message;
				});
		},
		saved(){
			setTimeout(()=>{
				this.saving = false;
			},500);
		},
		cancel(){
			this.selected = null;
		},
		remove(){
			if (confirm('Are you sure you want to delete ' + this.selection.title + '?')) {
				// tbd
			}
		},
		edit(value){
			this.selection.id = value ? value.id : null;
			this.selection.title = value ? value.title : null;
			this.selection.location.lat = value && value.location ? value.location.lat : null;
			this.selection.location.lng = value && value.location ? value.location.lng : null;
			this.selection.location.zoom = value && value.location ? value.location.zoom : null;
			this.selection.group_id = value ? value.group_id : null;
			this.selection.group =  value ? value.group : null;
			this.selection.type =  value ? value.type : null;
			this.$broadcast('set-location',value && value.location);
		}
	},
	events:{
		'map-center-changed': function(value){
			this.selection.location.lat = value.lat;
			this.selection.location.lng = value.lng;
		},
		'map-zoom-changed': function(value){
			this.selection.location.zoom = value;
		},
		'map-ready': function(){
			this.$broadcast('set-location', this.selection.location);
		},
		'coded-address': function(value){
			if(!this.selection.title){
				this.selection.title = value.address;
			}
		}
	},
	watch:{
		selected(value){
			this.edit(value);
		}
	}
})