DeveloperApp = new Marionette.Application();

DeveloperApp.addRegions({
  mainRegion: "#developerView"
});

DeveloperApp.SliceDetailView = Marionette.ItemView.extend({
  template: "#developer-slicedetail-template",
  tagName: 'tr',
  className: 'developer_slicedetail'
});

/*
DeveloperApp.SliceListView = Marionette.CollectionView.extend({
  tagName: "table",
  className: "table table-hover",
  template: "#developer-slicetable-template",
  childView: DeveloperApp.SliceDetailView,
});
*/

DeveloperApp.SliceListView = Marionette.CompositeView.extend({
  tagName: "table",
  className: "table-striped table-bordered",
  template: "#developer-slicetable-template",
  childView: DeveloperApp.SliceDetailView,
  childViewContainer: "tbody",
});

DeveloperApp.on("start", function() {
  var developerSliceListView = new DeveloperApp.SliceListView({
    collection: xos.slicesPlus
  });
  console.log(developerSliceListView);
  DeveloperApp.mainRegion.show(developerSliceListView);
  xos.slicesPlus.fetch();
});

$(document).ready(function(){
  DeveloperApp.start();
});

