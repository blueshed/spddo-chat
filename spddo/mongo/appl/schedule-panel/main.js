import './fullcalendar-scheduler-1.2.1/lib/fullcalendar.min.css!'
import './fullcalendar-scheduler-1.2.1/scheduler.min.css!'
import './main.css!'
import tmpl from "./main.html!text"

import Vue from 'vue'
import $ from 'jquery'
import moment from 'moment'
import _fc from './fullcalendar-scheduler-1.2.1/lib/fullcalendar.min'
import _fcs from './fullcalendar-scheduler-1.2.1/scheduler.min'

export default Vue.extend({
	props: ['selected_event', 'selected_asset'],
	template: tmpl,
	data(){
		return {
			title: '-',
			assets: null,
			allocations: null,
			view: 'timelineDay'
		}
	},
	ready(){
		this.load_assets().then(()=>{
			this.init_cal();
		});
	},
	methods:{
		select_asset(resource){
			this.selected_event = null;
			this.$nextTick(()=>{
				this.selected_asset = {
					_id: resource._id,
					id: resource.id,
					title: resource.title,
					location: resource.location,
					type: resource.type,
					group_id: resource.group_id
				};	
			});
		},
        select_event(values){
			this.selected_asset = null;
			this.$nextTick(()=>{
				this.selected_event = values;
			});
        },
		load_assets(){
			return this.control.assets().
				then((result)=>{
					this.assets = result.map((item)=>{
						return {
							_id: item._id,
							id: item.id,
							title: item.name,
							location: item.location,
							type: item.type,
							gorup_id: item.group_id
						};
					});
				}).
				catch((err)=>{
					this.$root.error = err;
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
					this.$root.error = err;
				});
		},
		do_select(start, end, jsEvent, view, resource){
			this.select_event({
				id: null,
				title: null,
				start: start,
				end: end,
				resource_id: resource ? resource.id : null,
				resource: resource ? resource.title : null
			});
		},
		do_unselect(view, jsEvent){
			this.selected_event = null;
		},
		do_event_click(event, jsEvent, view){
			if(this.view=="timelineDay"){
				var resource = event.resourceId ? this._cal.fullCalendar('getResourceById', event.resourceId) : null;
				this._cal.fullCalendar('unselect');
				this.select_event({
						_id: event._id,
						id: event.id,
						title: event.title,
						start: event.start,
						end: event.end,
						resource_id: resource ? resource.id : null,
						resource: resource ? resource.title : null
					});
			} 
			else{
				this.view = 'timelineDay';
				this._cal.fullCalendar('gotoDate',event.start);
			}
		},
        do_change(event, delta, revertFunc, jsEvent, ui, view){
			var resource = event.resourceId ? this._cal.fullCalendar('getResourceById', event.resourceId) : null;
			if(resource){
				this.select_event({
					_id: event._id,
					id: event.id,
					title: event.title,
					start: event.start,
					end: event.end,
					resource_id: resource ? resource.id : null,
					resource: resource ? resource.title : null
				});
			}
        },
		init_cal(){
			this._cal = $(this.$els.cal).fullCalendar({
				schedulerLicenseKey: 'CC-Attribution-NonCommercial-NoDerivatives',
				now: '2016-01-07',
				editable: true,
				aspectRatio: 1.8,
				scrollTime: '09:00',
				header: '',
				defaultView: this.view,
				views: {
					timelineFiveDay: {
						type: 'timeline',
						duration: { days: 5 }
					}
				},
				resourceLabelText: 'Assets',
				resourceRender: (resource, cellEls)=>{
					cellEls.on('click', this.select_asset.bind(this, resource));
				},
				selectable: true,
		        unselectAuto: false,
				select: this.do_select.bind(this),
				unselect: this.do_unselect.bind(this),
				resources: this.assets,
				events: this.load_allocations.bind(this),
				eventDrop: this.do_change.bind(this),
				eventResize: this.do_change.bind(this),
				eventClick: this.do_event_click.bind(this)
			});
			this.update_title();
		},
		go_next(){
			if(this._cal){
	            this._cal.fullCalendar('next');
	            this.update_title();
			}
        },
        go_prev(){
        	if(this._cal){
	            this._cal.fullCalendar('prev');
	            this.update_title();
        	}
        },
        go_today(){
        	if(this._cal){
	            this._cal.fullCalendar('today');
	            this.update_title();
        	}
        },
        update_title() {
        	var view = this._cal && this._cal.fullCalendar('getView');
            this.title = view ? view.title : "-";
        }
	},
	events:{
		"asset-added": function(asset){
			var item = {
				_id: asset._id,
				id: asset.id,
				title: asset.name,
				location: asset.location,
				type: asset.type,
				group_id: asset.group_id
			};
			this.assets.push(item);
			this._cal.fullCalendar("addResource", item);
		},
		"asset-changed": function(asset){
			var resource = this.assets.find((item)=>{
				return item.id == asset.id;
			});
			if(resource){
				resource._id = asset._id;
				resource.title = asset.name;
				resource.location = asset.location;
				resource.type = asset.type;
				resource.group_id = asset.group_id;
				this._cal.fullCalendar("refetchResources");
			}
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
					this.select_event({
						title: event.title,
						start: event.start,
						end: event.end,
						resource_id: event.resource ? event.resource.id : null,
						resource: event.resource ? event.resource.title : null
					})
				}
			}			
		}
	},
	watch:{
        view(value){
            if(this._cal){
                this._cal.fullCalendar('changeView',value);
	            this.update_title();
            }
        },
		selected_event(value){
			if(!value && this._cal){
				this._cal.fullCalendar('unselect');
			}
		}
	}
});