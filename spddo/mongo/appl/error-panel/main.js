import './main.css!';
import tmpl from './main.html!text';
import Vue from 'vue';

export default Vue.extend({
  	template: tmpl,
  	props: [
  		"error"
  	],
  	methods:{
    	clear_error: function(){
    		this.error = null;
    	}
  	}
});
