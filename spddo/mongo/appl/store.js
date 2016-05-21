import Vue from "vue"
import Vuex from "vuex"
import moment from "moment"

Vue.use(Vuex)

const state = {
	assets: [],
	allocations: [],
	user: null
}

const mutations = {
	MICRO_COOKIE_SET(state, user){
		state.user = user;
	},
	SET_ALLOCATIONS(state, allocations){
		state.allocations = allocations
	},
	ALLOCATION_ADDED(state, allocation){
		state.allocations.push(allocation)
	},
	ALLOCATION_CHANGED(state, allocation){
		var item = state.allocations.find(item=>item.id == allocation.id)
		if(item){
			item.title = allocation.title;
			item.from_date = allocation.from_date;
			item.to_date = allocation.to_date;
			item.asset_id = allocation.asset_id;
		}
	},
	ALLOCATION_REMOVED(state, allocation){
		var item = state.allocations.find(item=>item.id == allocation.id)
		if(item){
			state.allocations.splice(state.allocations.indexOf(item),1);
		}
	},
	SET_ASSETS(store, assets){
		store.assets = assets
	},
	ASSET_ADDED(state, asset){
		var item = {
			_id: asset._id,
			id: asset.id,
			title: asset.name,
			location: asset.location,
			type: asset.type,
			group_id: asset.group_id
		};
		state.assets.push(item);
	},
	ASSET_CHANGED(state, asset){
		var resource = state.assets.find(item => item.id == asset.id)
		if(resource){
			resource._id = asset._id;
			resource.title = asset.name;
			resource.location = asset.location;
			resource.type = asset.type;
			resource.group_id = asset.group_id;
		}
	}
}

export default new Vuex.Store({
	state,
	mutations
})