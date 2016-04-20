import './main.css!'
import tmpl from './main.html!text'
import Vue from 'vue'

import {google_loader, VENUE_ZOOM, code_address, geo_location} from '../google/map-utils'
var google_maps = null;

import MarkerComponent from "./marker"

export default Vue.extend({
  	template: tmpl,
  	props:["location"],
  	data(){
  		return {
  			loaded: false,
  			map_height: '320px',
  			map_width: '100%',
  			markers: [],
  			address: null,
  			tool: 'info',
  			silent: false,
  			busy: false
  		}
  	},
  	components:{
		"marker": MarkerComponent
  	},
  	methods:{
  		get_google_maps(){
  			return google_maps;
  		},
  		init_map(){
			if(this._map) return;
  			this._todo = null;
  			this.silent = true;
  			this._map = new google_maps.Map(this.$els.map,{
  				center: new google_maps.LatLng(this.location && this.location.lat || 51,
  											   this.location && this.location.lng || 0),
  				zoom: this.location && this.location.zoom || 7,
                mapTypeId: google_maps.MapTypeId.SATELLITE
  			});
  			
  			google_maps.event.addListener(this._map, 'dblclick', (e) => {
                if (this._to_do) {
                    clearTimeout(this._to_do);
                    this._to_do = null;
                }
            });
  			google_maps.event.addListener(this._map, 'click', (e) => {
                if (this._to_do == null) {
                	this._to_do = setTimeout(() => {
                		this._to_do = null;
                        this.$emit("map-clicked",{
                        	lat: e.latLng.lat(), 
                        	lng: e.latLng.lng()
                        });
                    }, 300);
                }
            });
  			var pending_reposition = null;
  			this._center_marker = new google_maps.Marker({
	            map: this._map,
	            position: this._map.getCenter(),
	            title: "center",
  				icon: "//maps.google.com/mapfiles/ms/icons/blue-dot.png"
  			});
  			google_maps.event.addListener(this._map, 'center_changed', (e) => {
  				if(!pending_reposition && this.silent !== true){
  					pending_reposition = this.$nextTick(()=>{
  						var location = this._map.getCenter();
  		  				this._center_marker.setPosition(location);
  		  				pending_reposition = null;
  	  		  			this.$dispatch('map-center-changed',{lat: location.lat(), lng: location.lng()});
  					});
  				}
	        });
  			google_maps.event.addListener(this._map, 'zoom_changed', (e) => {
  				if(this.silent !== true){
  					this.$dispatch('map-zoom-changed',this._map.getZoom());
  				}
	        });
            this.loaded = true;
            this.silent = true;
            this.$dispatch("map-ready", google_maps);
  			this.$broadcast("map-ready", google_maps);
  		},
  		resize() {
  			return;
		  	this.map_height = (window.innerHeight - this.$els.map.offsetTop - 6) + 'px';
  			if(this._map){
  				this.$nextTick(()=>{
  		            var center = this._map.getCenter();
  		            google_maps.event.trigger(this._map, 'resize');
  		            this._map.panTo(center);
  				});
  			}
        },
        geo_address(){
  			if(this._map){
  	        	this.busy = true;
  				geo_location(google_maps, this._map, 
  							 this.not_busy.bind(this));
  			}
  			return false;
        },
        code_address(){
  			if(this.address && this._map){
  	        	this.busy = true;
  				code_address(google_maps, this._map, this.address,
  						     (result)=>{
  								 this.address = result.address;
  						    	 this.$dispatch('coded-address',result);
  						    	 this.not_busy();
  						     },
  						     this.not_busy.bind(this));
  			}
  			return false;
        },
        not_busy(result){
        	this.busy = false;
        }
  	},
  	events:{
  		'marker-clicked': function(marker){
  			return true;
  		},
  		'marker-moved': function({marker, lat, lng}){
  			return true;
  		},
  		'set-location': function(value){
  			if(value && this._map){
  				this.silent = true;
  				var center = new google_maps.LatLng(this.location && this.location.lat || 51,
						   							this.location && this.location.lng || 0);
  				this._map.panTo(center);
  				this._map.setZoom(this.location && this.location.zoom || 7);
  				this._center_marker.setPosition(center);
  				this.silent = false;
  			}
  		}
  	},
  	beforeDestroy(){
  		if(this._map){
  			this._center_marker.setMap(null);
  			this._center_marker = null;
	        delete this._map;
	        this._map = null;
  		}
  	},
  	ready(){
  		google_loader().
	      	then((result)=>{
	  			google_maps = result.maps;
	  			setTimeout(()=>{
  		  			this.init_map();
  		  	    	this.resize();	
	  			},100);
	  		}).
	  		catch((err)=>{
	  			this.$root ? this.$root.error = err : console.error(err);
	  		});
  	}
})