/* eslint-disable guard-for-in, no-undef, space-before-blocks*/
/* This is an example that uses xoslib + marionette to display the developer
   view.

   For an example that uses xoslib + datatables, see xosDeveloper_datatables.js
*/

DeveloperApp = new Marionette.Application();

DeveloperApp.addRegions({
  mainRegion: '#developerView'
});

DeveloperApp.SliceDetailView = Marionette.ItemView.extend({
  template: '#developer-slicedetail-template',
  tagName: 'tr',
  className: 'developer_slicedetail'
});

DeveloperApp.SliceListView = Marionette.CompositeView.extend({
  tagName: 'table',
  className: 'table table-bordered table-striped',
  template: '#developer-slicetable-template',
  childView: DeveloperApp.SliceDetailView,
  childViewContainer: 'tbody',

  events: {'click .sort': 'changeSort'},

  initialize: function() {
    this.listenTo(this.collection, 'change', this._renderChildren);
  },

  changeSort: function(e) {
    parts = $(e.currentTarget).attr('id').split('-');
    order = parts[1];
    fieldName = parts[2];
    this.collection.sortVar = fieldName;
    this.collection.sortOrder = order;
    this.collection.sort();
  },

  attachHtml: function(compositeView, childView, index) {
    // The REST API will let admin users see everything. For the developer
    // view we still want to hide slices we are not members of.
    if(childView.model.get('sliceInfo').roles.length === 0) {
      return;
    }
    DeveloperApp.SliceListView.__super__.attachHtml(compositeView, childView, index);
  },
});

DeveloperApp.on('start', function() {
  var developerSliceListView = new DeveloperApp.SliceListView({
    collection: xos.slicesPlus
  });

  DeveloperApp.mainRegion.show(developerSliceListView);
  xos.slicesPlus.startPolling();
});

$(document).ready(function() {
  DeveloperApp.start();
});

