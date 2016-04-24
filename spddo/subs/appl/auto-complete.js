import Vue from 'vue'
import autoComplete from 'autocompete/auto-complete.js'
import 'autocompete/auto-complete.css!'

var _next_id=0;
function to_ids(store, items, label){
	return items.map((item)=>{
		var id = "ac_"+ ++_next_id;
		store[id] = item;
		return {
			id: id,
			label: item[label || 'name']
		};
	})
}

Vue.directive('auto-complete', {
	params: ['source','label','selected'],
  	twoWay: true,
  	bind: function () {
		// do preparation work
		// e.g. add event listeners or expensive stuff
		// that needs to be run only once
		this.ac = new autoComplete({
			  selector: this.el,
			  minChars: 2,
			  source: (term, callback)=>{
				  this._store = {};
				  this.params.source(term, (result)=>{
					  callback(to_ids(this._store, result));
				  });
			  },
			  renderItem: function (item, search){
				  // escape special characters
				  search = search.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
				  var re = new RegExp("(" + search.split(' ').join('|') + ")", "gi");
				  return '<div class="autocomplete-suggestion" data-val="' + item.label + '" data-key="' + item.id + '">' + item.label.replace(re, "<b>$1</b>") + '</div>';
			  },
			  onSelect: (e, term, item)=>{
				  var key = item.getAttribute('data-key');
				  if(this.params.selected){
					  this.params.selected(this._store[key]);
				  } else {
					  this.set(this._store[key]);
				  }
			  }
		});
  	},
  	update: function (newValue, oldValue) {
	  // do something based on the updated value
	  // this will also be called for the initial value
  	},
  	unbind: function () {
	  // do clean up work
	  // e.g. remove event listeners added in bind()
	  this.ac.destroy();
  	}
})