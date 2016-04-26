import Vue from 'vue'

var google_maps = null;

export default Vue.extend({
	props: ["item","tool"],
	methods:{
		make_marker(){
			this._marker = new google_maps.Marker({
	            map: this.$parent._map,
	            position: this.item.location,
				draggable: this.tool=="pointer"
	        });
			google_maps.event.addListener(this._marker, 'click', (e) => {
	            if (e.stop) { e.stop(); }
	            this.$dispatch("marker-clicked", { marker: this.item });
	        });
			google.maps.event.addListener(this._marker, 'dragend', (e) => {
	            var c = this._marker.getPosition();
	            this.$dispatch("marker-moved", {
		            	marker: this.item, 
		            	lat: c.lat(), 
		            	lng:c.lng()
		            }).
	            	then((result)=>{
	            		// ok
	            	}).
	            	catch((err)=>{
	            		this.$root.error = err.message;
	            	});
	        });
		}
	},
	events: {
		"map-ready": function(api){
			google_maps = api;
			this.make_marker();
		}
	},
	watch:{
		tool(value){
			if(this._marker){
				this._marker.setDraggable(value=='pointer');
			}
		},
		"item.location":{
			deep:true,
			handler: function(value){
				if(value && this._marker){
	    			this._marker.setPosition(
	    				new google_maps.LatLng(value.lat,
	    									   value.lng)
	    			);
				}
			}
		}
	},
	beforeDestroy(){
		this.close_info();
		if(this._marker){
	        this._marker.setMap(null);
	        this._marker = null;
		}
	},
	ready(){
		if(this.$parent._map){
			google_maps = this.$parent.get_google_maps();
			this.make_marker();
		}
	}
});