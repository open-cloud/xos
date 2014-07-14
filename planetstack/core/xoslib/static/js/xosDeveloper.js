DeveloperApp = new Marionette.Application();

DeveloperApp.addRegions({
  mainRegion: "#developerView"
});

DeveloperApp.SliceDetailView = Marionette.ItemView.extend({
  template: "#developer-slicedetail-template",
  tagName: 'tr',
  className: 'developer_slicedetail'
});

DeveloperApp.SliceListView = Marionette.CompositeView.extend({
  tagName: "table",
  className: "table-striped table-bordered",
  template: "#developer-slicetable-template",
  childView: DeveloperApp.SliceDetailView,
  childViewContainer: "tbody",

  events: {"click .sort": "changeSort"},

  changeSort: function(e) {
      parts=$(e.currentTarget).attr("id").split('-');
      order=parts[1];
      fieldName=parts[2];
      console.log(fieldName);
      this.collection.sortVar = fieldName;
      this.collection.sortOrder = order;
      this.collection.sort();
  }
});

DeveloperApp.on("start", function() {
  var developerSliceListView = new DeveloperApp.SliceListView({
    collection: xos.slicesPlus
  });
  console.log(developerSliceListView);
  DeveloperApp.mainRegion.show(developerSliceListView);
  xos.slicesPlus.startPolling();
});

$(document).ready(function(){
  DeveloperApp.start();
});

