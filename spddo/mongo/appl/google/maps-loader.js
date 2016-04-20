var googleApi;
var loading;

function loadAutoCompleteAPI(params) {
	params = params ? params : {};
	params["key"] = "AIzaSyDLLK3zM_Qbe2EbslOtSHGA-PwyVla0T0Y";
	params["callback"] = "googleMapsAutoCompleteAPILoad";
  var script = document.createElement('script');
  script.type = 'text/javascript';
  script.src = '//maps.googleapis.com/maps/api/js?' + Object.keys(params).map(function(key){
	  return  encodeURIComponent(key) + '=' + encodeURIComponent(params[key]);
  }).join("&");
  document.querySelector('head').appendChild(script);
}

function googleMapsApiLoader(params) {
  if (googleApi) {
    return Promise.resolve(googleApi);
  }
  if(loading){
	  return loading;
  }
  var windowRef = window ? window : {};
  var deferred = function(resolve, reject) {
    loadAutoCompleteAPI(params);
    windowRef.googleMapsAutoCompleteAPILoad = function() {
    	googleApi = windowRef.google;
      	loading = null;
      	resolve(googleApi);
    };
    setTimeout(function() {
      if (!windowRef.google) {
    	  loading = null;
    	  reject(new Error('Loading took too long'));
      }
    }, 5000);
  };
  loading = new Promise(deferred);
  return loading;
}

export default googleMapsApiLoader;
