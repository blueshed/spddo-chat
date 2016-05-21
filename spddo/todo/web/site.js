
Control.prototype.install = function(Vue){
	Vue.prototype.$control = this;
};

Vue.config.debug = true;

Vue.use(new Control());

Vue.filter('moment', (value, format)=>{
	if(value){
		return moment(value).format(format || 'Do MMM YYYY h:mm a')  
	}
});

Vue.component('todo-list', {
	template: "#todo-list",
	data(){
		return {
			todo_id: null,
			todo_description: null,
			todo_created: null,
			todo_done: null
		};
	},
	methods:{
		add_todo(){
			this.$control.save_todo(this.todo_description).
				then((result)=>{
					this.clear();
				}).
				catch((err)=>{
					this.$root.error = err.message;
				})			
		},
		done_todo(){
			this.todo_done = moment().format("YYYY-MM-DD HH:mm:ss");
			this.save_todo();
		},
		not_done_todo(){
			this.todo_done = null;
			this.save_todo();
		},
		save_todo(){
			this.$control.save_todo(this.todo_description, 
								    this.todo_done,
								    this.todo_id).
				then((result)=>{
					this.clear();
				}).
				catch((err)=>{
					this.$root.error = err.message;
				})			
		},
		edit_todo(item){
			this.todo_description = item.description;
			this.todo_created = item.created;
			this.todo_done = item.done;
			this.todo_id = item.id;
		},
		clear(){
			this.todo_description = null;
			this.todo_created = null;
			this.todo_done = null;
			this.todo_id = null;
		},
		load(){
			this.$control.filter_todos("%").
				then((result)=>{
					this.$store.dispatch("SET_TODOs", result);
				}).
				catch((err)=>{
					this.$root.error = err.message;
				})	
		}
	},
	created(){
		this.load();
	},
	vuex: {
		getters: {
			todos(state) {
				return state.todos.slice().sort((a,b)=>{
					if(a.done && b.done){
						return moment(a.done).isBefore(b.done)
					}
					else if(a.done){
						return 1
					} else if(b.done){
						return -1
					}
					return moment(b.created).isBefore(a.created)
				})
		    }
		}
	}
});

var appl = window.appl = new Vue({
	el: ".main",
	data:{
		title: "Welcome",
		status: null,
		error: null,
		email: null,
		password: null
	},
	store: x_store,
	created: function(){
		this.$store.dispatch("MICRO_COOKIE_SET", this.$control._user);
		this.$control.init((signal, message)=>{
					this.$store.dispatch(signal, message);
				}).
			then((status)=>{
				this.status = status;
			}).
			catch((err)=>{
				this.error = err;
			});
	},
	methods:{
		login: function(){
			this.$control.login(this.email, this.password).
				then((result)=>{
					this.email = null;
					this.password = null;
				}).
				catch((err)=>{
					this.error = err.message;
				})
		}
	},
	vuex: {
		getters: {
		    user(state) {
		    	return state.user
		    }
		}
	}
});