import tmpl from './main.html!text'
import Vue from 'vue'

export default Vue.extend({
	props:['user'],
	template: tmpl,
	data:function(){
		return {
			email: null,
			password: null,
			error: null
		}
	},
	methods:{
		login: function(){
			this.control.login(this.email, this.password).
				then(function(user){
					this.user = user;
				}.bind(this)).
				catch(function(err){
					this.error = err;
				}.bind(this));
		}
	}
});
