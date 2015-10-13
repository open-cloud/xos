
var ContactManager = new Marionette.Application();

ContactManager.addRegions({
  mainRegion: '#main-region'
});

ContactManager.Contact = Backbone.Model.extend({});

ContactManager.ContactCollection = Backbone.Collection.extend({
  model: ContactManager.Contact
});

ContactManager.ContactItemView = Marionette.ItemView.extend({
  tagName: 'li',
  template: '#contact-list-item'
});

ContactManager.ContactsView = Marionette.CollectionView.extend({
  tagName: 'ul',
  childView: ContactManager.ContactItemView
});

ContactManager.on('start', function() {
  var contacts = new ContactManager.ContactCollection([
    {
      firstName: 'Bob',
      lastName: 'Brigham',
      phoneNumber: '555-0163'
    },
    {
      firstName: 'Alice',
      lastName: 'Arten',
      phoneNumber: '555-0184'
    },
    {
      firstName: 'Charlie',
      lastName: 'Campbell',
      phoneNumber: '555-0129'
    }
  ]);

  var contactsView = new ContactManager.ContactsView({
    collection: contacts
  });

  ContactManager.mainRegion.show(contactsView);
});

ContactManager.start();
