var x_state = {
	todos : [],
	user : null
};

var x_mutations = {
	MICRO_COOKIE_SET(state, user){
		state.user = user;
	},
	SET_TODOs(state, todos){
		state.todos = todos;
	},
	SAVED_TODO : function(state, data) {
		var todo = state.todos.find(item => item.id === data.id)
		if (todo) {
			Object.keys(data).map((key)=>{
				Vue.set(todo,key,data[key]);
			})
		} else {
			state.todos.push(data);
		}
	}
};


var x_store = new Vuex.Store({
	state : x_state,
	mutations : x_mutations,
	strict : true
});
