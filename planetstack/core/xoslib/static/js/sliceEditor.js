SliceEditorApp = new Marionette.Application();

SliceEditorApp.addRegions({
  sliceList: "#sliceEditorList",
  sliceDetail: "#sliceEditorDetail",
});

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

        var sliceDetailView = new SliceEditorApp.SliceDetailView({
            model: this.model,
        });
        SliceEditorApp.sliceDetail.show(sliceDetailView);
  },
});

SliceEditorApp.SliceListView = Marionette.CollectionView.extend({
  tagName: "ul",
  childView: SliceEditorApp.SliceListItemView,

  modelEvents: {"sync": "render"},

  initialize: function() {
      this.dirty = false;
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

SliceEditorApp.SliceDetailView = Marionette.ItemView.extend({
    template: "#sliceeditor-sliceedit-template",
    tagName: 'div',

    events: {"click button.js-submit": "submitClicked",
             "change input": "inputChanged"},

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

