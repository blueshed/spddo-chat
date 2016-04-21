
import google_loader from './maps-loader'

export const VENUE_ZOOM = 16;

export {google_loader as google_loader};

export function geo_location(google_maps, map, callback){
	if (navigator.geolocation){
		navigator.geolocation.getCurrentPosition((position)=>{
			map.setCenter(new google_maps.LatLng(
					position.coords.latitude,
					position.coords.longitude));
            map.setZoom(VENUE_ZOOM);
            if(callback){
                callback(position);
            }
		});
    }
	else{
		this.$root.error("Geolocation is not supported by this browser.");
        if(callback){
            callback(null);
        }
	}
}
        
export function code_address(google_maps, map, address, callback, errback){
    if(!address){
        if(callback){
            callback(null);
        }
        return;
    }
    var geocoder = new google_maps.Geocoder();
    geocoder.geocode( { 'address': address }, (results, status)=>{
        if (status == google_maps.GeocoderStatus.OK) {
        	map.setCenter(results[0].geometry.location);
            map.setZoom(VENUE_ZOOM);
            if(callback){
                callback({
                	location: results[0].geometry.location, 
                	address: results[0].formatted_address, 
                	raw: results[0]
                });
            }
        } else if(errback){
    		errback("Geocode error: " + status)
    	}
    });
}