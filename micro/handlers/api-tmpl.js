{% autoescape None %}{% whitespace all %}
function uid() {
    function _p8(s) {
        var p = (Math.random().toString(16)+"000000000").substr(2,8);
        return s ? "-" + p.substr(0,4) + "-" + p.substr(4,4) : p ;
    }
    return _p8() + _p8(true);
}
var docCookies = {
  getItem: function (sKey,escape) {
    if (!sKey) { return null; }
    var result = document.cookie.replace(new RegExp("(?:(?:^|.*;)\\s*" + encodeURIComponent(sKey).replace(/[\-\.\+\*]/g, "\\$&") + "\\s*\\=\\s*([^;]*).*$)|^.*$"), "$1") || null;
    if(result && escape !== false){
    	result = decodeURIComponent(result);
    }
    return result;
  },
  setItem: function (sKey, sValue, vEnd, sPath, sDomain, bSecure, escape) {
    if (!sKey || /^(?:expires|max\-age|path|domain|secure)$/i.test(sKey)) { return false; }
    var sExpires = "";
    if (vEnd) {
      switch (vEnd.constructor) {
        case Number:
          sExpires = vEnd === Infinity ? "; expires=Fri, 31 Dec 9999 23:59:59 GMT" : "; max-age=" + vEnd;
          break;
        case String:
          sExpires = "; expires=" + vEnd;
          break;
        case Date:
          sExpires = "; expires=" + vEnd.toUTCString();
          break;
      }
    }
    if(escape !== false){
    	sValue = encodeURIComponent(sValue);
    }
    document.cookie = encodeURIComponent(sKey) + "=" + sValue + sExpires + (sDomain ? "; domain=" + sDomain : "") + (sPath ? "; path=" + sPath : "") + (bSecure ? "; secure" : "");
    return true;
  },
  removeItem: function (sKey, sPath, sDomain) {
    if (!this.hasItem(sKey)) { return false; }
    document.cookie = encodeURIComponent(sKey) + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT" + (sDomain ? "; domain=" + sDomain : "") + (sPath ? "; path=" + sPath : "");
    return true;
  },
  hasItem: function (sKey) {
    if (!sKey) { return false; }
    return (new RegExp("(?:^|;\\s*)" + encodeURIComponent(sKey).replace(/[\-\.\+\*]/g, "\\$&") + "\\s*\\=")).test(document.cookie);
  },
  keys: function () {
    var aKeys = document.cookie.replace(/((?:^|\s*;)[^\=]+)(?=;|$)|^\s*|\s*(?:\=[^;]*)?(?:\1|$)/g, "").split(/\s*(?:\=[^;]*)?;\s*/);
    for (var nLen = aKeys.length, nIdx = 0; nIdx < nLen; nIdx++) { aKeys[nIdx] = decodeURIComponent(aKeys[nIdx]); }
    return aKeys;
  }
};


function Control(){}
    
Control.prototype.init = function(broadcast_callback){
	var client_id = uid();
	var last_id = 0;
	var promises = {};
	return new Promise(function(resolve,reject){
		var ws = null;
		try{
			ws = new WebSocket('{{ handler.application.settings['ws_url'] }}' + "?client_id="+client_id);
		}
		catch(err){
			reject(err);
		}
		ws.onopen = function(){
			this.connection = ws;
			resolve('open');
		}.bind(this);
		ws.onmessage = function(evt){
			var message = JSON.parse(evt.data);
			if(message.cookie){
	            var expires = new Date();
	            expires.setMonth(expires.getMonth() + 1);
	            docCookies.setItem(message.cookie_name, message.cookie, expires.toGMTString(),null,null,null,false);
			}
			if(promises[message.id]){
				if(message.error){
					promises[message.id].reject(message.error);
				} else {
					promises[message.id].resolve(message.result);
				}
				delete promises[message.id];
			} else if(message.signal, broadcast_callback){
				broadcast_callback(message.signal, message.message);
			} else {
				console.log(message);
			}
		}.bind(this);
		ws.onclose = function(){
			this.connection = null;
			setTimeout(function(){
				location.reload(true);
			},200);
		}.bind(this);
		ws.onerror = function(err){
			if(!this.connection){
				reject(err.code || 'unknown error');
			}
		}.bind(this);
		ws.rpc = function(action, args){
			return new Promise(function(resolve,reject){
				var id = client_id + ":"+ ++last_id;
				ws.send(JSON.stringify([id,action,args]));
				promises[id] = { reject: reject, resolve: resolve };
			}.bind(this));
		}.bind(this);
	}.bind(this))
};

Control.prototype._send = function(action, args, callback) {
	if(!this.connection){
		throw "Not connected!";
	}
	return this.connection.rpc(action, args);
};
	
{% for service in services %}
{% if service.docs %}/** 
	{{ service.docs }}
**/{% end %}
Control.prototype.{{ service.name }} = function({{ ", ".join([p.name for p in service.desc.parameters.values() if p.name[0] != '_' and p.name != 'context']) }}){
	return this._send("{{ service.name }}", { 
		{{ ",\n\t\t".join(["{0!r}: {0}{1}".format(p.name,'|| ' + repr(p.default) if p.default is not p.empty else '') for p in service.desc.parameters.values() if p.name[0] != '_' and p.name != 'context']) }} 
	});
};
{% end %}