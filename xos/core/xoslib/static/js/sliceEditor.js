/* eslint-disable */
/* This is a demo of using xoslib with Marionette

   The main window is split into two halves. The left half has a CollectionView
   (SliceListView) that lists all slices the user has access to. The right half
   has an ItemView (SliceDetailView) that allows the user to edit the
   name and description of a slice, as well as a <Save> button to save it.
*/

SliceEditorApp = new Marionette.Application();

SliceEditorApp.addRegions({
  sliceList: "#sliceEditorList",
  sliceDetail: "#sliceEditorDetail",
});

/* SliceListItemView: This is the item view that is used by SliceListView to
   display slice names.
*/

SliceEditorApp.SliceListItemView = Marionette.ItemView.extend({
  template: "#sliceeditor-listitem-template",
  tagName: 'li',
  className: 'sliceeditor-listitem',

  events: {"click": "changeSlice"},

  changeSlice: function(e) {
        e.preventDefault();
        e.stopPropagation();

        if (SliceEditorApp.sliceDetail.currentView && SliceEditorApp.sliceDetail.currentView.dirty) {
            if (!confirm("discard current changes?")) {
                return;
            }
        }

        /* create a new SliceDetailView and set the sliceDetail region to
           display it.
        */

        var sliceDetailView = new SliceEditorApp.SliceDetailView({
            model: this.model,
        });
        SliceEditorApp.sliceDetail.show(sliceDetailView);
  },
});

/* SliceListView: This displays a list of slice names.
*/

SliceEditorApp.SliceListView = Marionette.CollectionView.extend({
  tagName: "ul",
  childView: SliceEditorApp.SliceListItemView,

  initialize: function() {
      /* CollectionViews don't automatically listen for change events, but we
         want to, so we pick up changes from the DetailView, and we pick up
         changes from the server.
      */
      this.listenTo(this.collection, 'change', this._renderChildren);
  },

  attachHtml: function(compositeView, childView, index) {
      // The REST API will let admin users see everything. For the developer
      // view we still want to hide slices we are not members of.
      if (childView.model.get("sliceInfo").roles.length == 0) {
          return;
      }
      SliceEditorApp.SliceListView.__super__.attachHtml(compositeView, childView, index);
  },
});

/* SliceDetailView: Display the slice and allow it to be edited */

SliceEditorApp.SliceDetailView = Marionette.ItemView.extend({
    template: "#sliceeditor-sliceedit-template",
    tagName: 'div',

    events: {"click button.js-submit": "submitClicked",
             "change input": "inputChanged"},

    /* inputChanged is watching the onChange events of the input controls. We
       do this to track when this view is 'dirty', so we can throw up a warning
       if the user tries to change his slices without saving first.
    */

    inputChanged: function(e) {
        this.dirty = true;
    },

    submitClicked: function(e) {
        e.preventDefault();
        var data = Backbone.Syphon.serialize(this);
        this.model.save(data);
        this.dirty = false;
    },
});

SliceEditorApp.on("start", function() {
  var sliceListView = new SliceEditorApp.SliceListView({
    collection: xos.slicesPlus
  });
  SliceEditorApp.sliceList.show(sliceListView);
  xos.slicesPlus.startPolling();
});

$(document).ready(function(){
  SliceEditorApp.start();
});
/* eslint-enable */
