DeveloperApp = new Marionette.Application();

DeveloperApp.addRegions({
  mainRegion: "#developerView"
});

DeveloperApp.SliceDetailView = Marionette.ItemView.extend({
  template: "#developer-slicedetail-template",
  tagName: 'tr',
  className: 'developer_slicedetail'
});

DeveloperApp.SliceListView = Marionette.CollectionView.extend({
  tagName: "table",
  className: "table-striped table-bordered",
  template: "#developer-slicetable-template",
  childView: DeveloperApp.SliceDetailView,
});

DeveloperApp.on("start", function() {
  var developerSliceListView = new DeveloperApp.SliceListView({
    collection: xos.slices
  });
  console.log(developerSliceListView);
  DeveloperApp.mainRegion.show(developerSliceListView);
  xos.slices.fetch();
});

$(document).ready(function(){
  DeveloperApp.start();
});

