DeveloperApp = new Marionette.Application();

DeveloperApp.addRegions({
  mainRegion: "#developerView"
});

DeveloperApp.SlioeDetailView = Marionette.ItemView.extend({
  template: "#developer-slicedetail-template",
  tagName: 'tr',
  className: 'developer_slicedetail'
});

DeveloperApp.ContactsView = Marionette.CollectionView.extend({
    tagName: "table",
    childView: DeveloperApp.ContactItemView
});

DeveloperApp.on("start", function(){
    xos.slices.add(        {
            firstName: "Bob",
            lastName: "Brigham",
            phoneNumber: "555-0163"
        });

    var contactsView = new DeveloperApp.ContactsView({
        collection: xos.slices
    });

    DeveloperApp.mainRegion.show(contactsView);
});

$(document).ready(function(){
   DeveloperApp.start();
});
