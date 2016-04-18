Control.prototype.install = function(Vue){
	Vue.prototype.control = this;
};

Vue.config.debug = true;

Vue.use(new Control());

Vue.filter('moment', function (value, format) {
	if(value){
		return moment(value).format(format || 'Do MMM YYYY')  
	}
});


var appl = window.appl = new Vue({
	el: ".container",
	data:{
		status: null,
		error: null,
		user: null,
		assets: null,
		allocations: null,
		selection: {}
	},
	computed:{
		can_allocated: function(){
			return this.selection.title;
		}
	},
	created(){
		this.control.init(function(signal, message){
				this.$dispatch(signal, message);
				this.$broadcast(signal, message);
			}.bind(this)).
		then(function(status){
			this.status = status;
			this.load_assets().then(function(){
				this.init_cal();
			}.bind(this));
		}.bind(this)).
		catch(function(err){
			this.error = err;
		}.bind(this));
	},
	methods:{
		add_asset: function(){
			var title = prompt('Asset name');
			if (title) {
				this.control.add_asset({
					id: uid(),
					name: title
				}).
				then(function(status){
					// noop
				}.bind(this)).
				catch(function(err){
					this.error = err;
				}.bind(this));
			}
		},
		remove_asset: function(resource){
			if (confirm('Are you sure you want to delete ' + resource.title + '?')) {
				this._cal.fullCalendar('removeResource', resource);
			}
		},
		load_assets: function(){
			return this.control.assets().
				then(function(result){
					this.assets = result.map(function(item){
						return {
							_id: item._id,
							id: item.id,
							title: item.name
						};
					});
				}.bind(this)).
				catch(function(err){
					this.error = err;
				}.bind(this));
		},
		allocate: function(){
			this.control.allocate({
					id: uid(),
					title: this.selection.title,
					from_date: this.selection.start.unix(),
					to_date: this.selection.end.unix(),
					asset_id: this.selection.resource_id
				}).
				then(function(result){
					this.clear_selection();
				}.bind(this)).
				catch(function(err){
					this.error = err;
				}.bind(this));
			
		},
		unallocate: function(){
			this.control.unallocate(this.selection.id).
				then(function(result){
					this.clear_selection();
				}.bind(this)).
				catch(function(err){
					this.error = err;
				}.bind(this));
		},
		load_allocations: function(start, end, timezone, callback){
			this.control.allocations(start.unix(), end.unix()).
				then(function(result){
					this.allocations = result.map(function(item){
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
				}.bind(this)).
				catch(function(err){
					this.error = err;
				}.bind(this));
		},
		do_select: function(start, end, jsEvent, view, resource){
			this.set_selection({
				id: null,
				title: null,
				start: start,
				end: end,
				resource_id: resource ? resource.id : null,
				resource: resource ? resource.title : null
			});
		},
		do_unselect: function(view, jsEvent){
			this.set_selection({
				id: null,
				title: null,
				start: null,
				end: null,
				resource_id: null,
				resource: null
			});
		},
		clear_selection: function(){
			this.do_unselect();
			this._cal.fullCalendar('unselect');
		},
        set_selection: function(values){
        	Object.keys(values).map(function(key){
        		this.$set("selection."+key,values[key]);
        	}.bind(this));
        },
        do_change: function(event, delta, revertFunc, jsEvent, ui, view){
        	this.control.change_allocation({
        		_id: event._id,
        		id: event.id,
        		title: event.title,
        		from_date: event.start.unix(),
        		to_date: event.end.unix(),
        		asset_id: event.resourceId
        	});
        },
		init_cal: function(){
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
				resourceRender: function(resource, cellEls) {
					cellEls.on('click', this.remove_asset.bind(this, resource));
				}.bind(this),
				selectable: true,
		        unselectAuto: false,
				select: this.do_select.bind(this),
				unselect: this.do_unselect.bind(this),
				resources: this.assets,
				events: this.load_allocations.bind(this),
				eventDrop: this.do_change.bind(this),
				eventResize: this.do_change.bind(this),
				eventClick: function( event, jsEvent, view ){ 
					this.set_selection({
						_id: event._id,
						id: event.id,
						title: event.title,
						start: event.start,
						end: event.end,
						resource_id: event.resource ? event.resource.id : null,
						resource: event.resource ? event.resource.title : null
					})
				}.bind(this)
			});		
			$(".fc-widget-header>div>.fc-cell-content>span.fc-cell-text").
				append($("<span>").
						addClass("fa fa-plus pull-right add-asset-icon").
						click(function(){
								this.add_asset();
							}.bind(this)));
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
			this._cal.fullCalendar( 'removeEvents', function(item){
				return item.id == allocation_id;
			});
		},
		"allocation-changed": function(allocation){
			var events = this._cal.fullCalendar( 'clientEvents', function(item){
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