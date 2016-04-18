import './fullcalendar-scheduler-1.2.1/lib/fullcalendar.min.css!'
import './fullcalendar-scheduler-1.2.1/scheduler.min.css!'
import './main.css!'
import tmpl from "./main.html!text"

import Vue from 'vue'
import './moment-filter'
import $ from 'jquery'
import moment from 'moment'
import _fc from './fullcalendar-scheduler-1.2.1/lib/fullcalendar.min'
import _fcs from './fullcalendar-scheduler-1.2.1/scheduler.min'

export default Vue.extend({
	template: tmpl,
	data(){
		return {
			assets: null,
			allocations: null,
			selection: {}
		}
	},
	computed:{
		can_allocated(){
			return this.selection.title;
		}
	},
	ready(){
		this.load_assets().then(()=>{
			this.init_cal();
		});
	},
	methods:{
		uid() {
		    function _p8(s){
		        var p = (Math.random().toString(16)+"000000000").substr(2,8);
		        return s ? "-" + p.substr(0,4) + "-" + p.substr(4,4) : p ;
		    }
		    return _p8() + _p8(true);
		},
		add_asset(){
			var title = prompt('Asset name');
			if (title) {
				this.control.save_asset({
					id: this.uid(),
					name: title
				}).
				then((status)=>{
					// noop
				}).
				catch((err)=>{
					this.error = err;
				});
			}
		},
		remove_asset(resource){
			if (confirm('Are you sure you want to delete ' + resource.title + '?')) {
				this._cal.fullCalendar('removeResource', resource);
			}
		},
		load_assets(){
			return this.control.assets().
				then((result)=>{
					this.assets = result.map((item)=>{
						return {
							_id: item._id,
							id: item.id,
							title: item.name
						};
					});
				}).
				catch((err)=>{
					this.error = err;
				});
		},
		allocate(){
			this.control.allocate({
					id: this.selection.id || this.uid(),
					title: this.selection.title,
					from_date: this.selection.start.unix(),
					to_date: this.selection.end.unix(),
					asset_id: this.selection.resource_id
				}).
				then((result)=>{
					this.clear_selection();
				}).
				catch((err)=>{
					this.error = err;
				});
		},
		unallocate(){
			this.control.unallocate(this.selection.id).
				then((result)=>{
					this.clear_selection();
				}).
				catch((err)=>{
					this.error = err;
				});
		},
		load_allocations(start, end, timezone, callback){
			this.control.allocations(start.unix(), end.unix()).
				then((result)=>{
					this.allocations = result.map((item)=>{
						return {
							_id: item._id,
							id: item.id,
							title: item.title,
							start: moment.unix(item.from_date),
							end: moment.unix(item.to_date),
							resourceId: item.asset_id
						}
					});
					callback(this.allocations);
				}).
				catch((err)=>{
					this.error = err;
				});
		},
		do_select(start, end, jsEvent, view, resource){
			this.set_selection({
				id: null,
				title: null,
				start: start,
				end: end,
				resource_id: resource ? resource.id : null,
				resource: resource ? resource.title : null
			});
		},
		do_unselect(view, jsEvent){
			this.set_selection({
				id: null,
				title: null,
				start: null,
				end: null,
				resource_id: null,
				resource: null
			});
		},
		clear_selection(){
			this.do_unselect();
			this._cal.fullCalendar('unselect');
		},
        set_selection(values){
        	Object.keys(values).map((key)=>{
        		this.$set("selection."+key,values[key]);
        	});
        },
        do_change(event, delta, revertFunc, jsEvent, ui, view){
        	this.control.allocate({
        		id: event.id,
        		title: event.title,
        		from_date: event.start.unix(),
        		to_date: event.end.unix(),
        		asset_id: event.resourceId
        	}).
			then((result)=>{
				// noop
			}).
			catch((err)=>{
				this.error = err;
			});
        },
		init_cal(){
			this._cal = $('.calendar').fullCalendar({
				schedulerLicenseKey: 'CC-Attribution-NonCommercial-NoDerivatives',
				now: '2016-01-07',
				editable: true,
				aspectRatio: 1.8,
				scrollTime: '09:00',
				header: {
					left: 'title',
					right: 'promptResource timelineDay,timelineThreeDays,agendaWeek,month today prev,next'
				},
				customButtons: {
					promptResource: {
						text: '+ Asset',
						click: this.add_asset.bind(this)
					}
				},
				defaultView: 'timelineDay',
				views: {
					timelineThreeDays: {
						type: 'timeline',
						duration: { days: 3 }
					}
				},
				resourceLabelText: 'Assets',
				resourceRender: (resource, cellEls)=>{
					cellEls.on('click', this.remove_asset.bind(this, resource));
				},
				selectable: true,
		        unselectAuto: false,
				select: this.do_select.bind(this),
				unselect: this.do_unselect.bind(this),
				resources: this.assets,
				events: this.load_allocations.bind(this),
				eventDrop: this.do_change.bind(this),
				eventResize: this.do_change.bind(this),
				eventClick: ( event, jsEvent, view )=>{
					var resource = event.resourceId ? this._cal.fullCalendar('getResourceById', event.resourceId) : null;
					this.set_selection({
						_id: event._id,
						id: event.id,
						title: event.title,
						start: event.start,
						end: event.end,
						resource_id: resource ? resource.id : null,
						resource: resource ? resource.title : null
					})
				}
			});		
			$(".fc-widget-header>div>.fc-cell-content>span.fc-cell-text").
				append($("<span>").
						addClass("fa fa-plus pull-right add-asset-icon").
						click((item)=>{
								this.add_asset();
							}));
		}
	},
	events:{
		"asset-added": function(asset){
			this._cal.fullCalendar("addResource", {
				_id: asset._id,
				id: asset.id,
				title: asset.name
			});
			this.assets.push(asset);
		},
		"allocation-added": function(allocation){
			this._cal.fullCalendar("refetchEvents");
		},
		"allocation-removed": function(allocation_id){
			this._cal.fullCalendar( 'removeEvents', (item)=>{
				return item.id == allocation_id;
			});
		},
		"allocation-changed": function(allocation){
			var events = this._cal.fullCalendar( 'clientEvents', (item)=>{
				return item.id == allocation.id;
			});
			if(events && events.length==1){
				var event = events[0];
				event.title = allocation.title;
				event.start = moment.unix(allocation.from_date);
				event.end = moment.unix(allocation.to_date);
				event.resourceId = allocation.asset_id;
				this._cal.fullCalendar("updateEvent", event);
				if(this.selection && this.selection.id == allocation.id){
					this.set_selection({
						title: event.title,
						start: event.start,
						end: event.end,
						resource_id: event.resource ? event.resource.id : null,
						resource: event.resource ? event.resource.title : null
					})
				}
			}			
		}
	}
});