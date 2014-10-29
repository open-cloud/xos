TestApp = new Marionette.Application();

TestApp.addRegions({
    deploymentList: "#deploymentList",
    imageList: "#imageList",
    networkTemplateList: "#networkTemplateList",
    networkList: "#networkList",
    nodeList: "#nodeList",
    serviceList: "#serviceList",
    siteList: "#siteList",
    sliceList: "#sliceList",
    sliverList: "#sliverList",
    userList: "#userList",
    detail: "#detail"
});

// ---- Deployment ----

TestApp.DeploymentListItemView = Marionette.ItemView.extend({
    template: '#test-deployment-listitem-template',
    tagName: 'tr',
    className: 'test-tablerow',
});

TestApp.DeploymentListView = Marionette.CompositeView.extend({
    childView: TestApp.DeploymentListItemView,
    childViewContainer: 'tbody',
    template: '#test-deployment-list-template',

    initialize: function() {
        this.listenTo(this.collection, 'change', this._renderChildren)
    },
});

TestApp.hideError = function(result) {
    $("#errorBox").hide();
    $("#successBox").hide();
};

TestApp.showSuccess = function(result) {
     $("#successBox").show();
     $("#successBox").html(_.template($("#test-success-template").html())(result));
     $('#close-success-box').unbind().bind('click', function() {
         $('#successBox').hide();
     });
};

TestApp.showError = function(result) {
     $("#errorBox").show();
     $("#errorBox").html(_.template($("#test-error-template").html())(result));
     $('#close-error-box').unbind().bind('click', function() {
         $('#errorBox').hide();
     });
};

TestApp.on("start", function() {
     var objs = ['deployment', 'image', 'networkTemplate', 'network', 'node', 'service', 'site', 'slice', 'sliver', 'user'];

     for (var index in objs) {
         name = objs[index];
         tr_template = '#test-' + name + '-listitem-template';
         table_template = '#test-' + name + '-list-template';
         detail_template = '#test-' + name + '-detail-template';
         collection_name = name + "s";
         region_name = name + "List";

         detailClass = Marionette.ItemView.extend({
            template: detail_template,
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

            saveError: function(model, result, xhr) {
                TestApp.showError(result);
            },

            saveSuccess: function(model, result, xhr) {
                TestApp.showSuccess({status: xhr.xhr.status, statusText: xhr.xhr.statusText});
            },

            submitClicked: function(e) {
                TestApp.hideError();
                e.preventDefault();
                var data = Backbone.Syphon.serialize(this);
                var thisView = this;
                this.model.save(data, {error: function(model, result, xhr) { thisView.saveError(model, result, xhr); },
                                       success: function(model, result, xhr) { thisView.saveSuccess(model, result, xhr); }});
                this.dirty = false;
            },
         });

         itemViewClass = Marionette.ItemView.extend({
             detailClass: detailClass,
             template: tr_template,
             tagName: 'tr',
             className: 'test-tablerow',

             events: {"click": "changeItem"},

             changeItem: function(e) {
                    TestApp.hideError();
                    e.preventDefault();
                    e.stopPropagation();

                    var detailView = new this.detailClass({
                        model: this.model,
                    });
                    $('#detailBox').show();
                    TestApp.detail.show(detailView);
              },
         });

         listViewClass = Marionette.CompositeView.extend({
             childView: itemViewClass,
             childViewContainer: 'tbody',
             template: table_template,
             collection: xos[collection_name],

             initialize: function() {
                 this.listenTo(this.collection, 'change', this._renderChildren)
             },
         });

         var listView = new listViewClass();

         TestApp[region_name].show(listView);
         xos[collection_name].fetch(); //startPolling();
     }

     $('#close-detail-view').unbind().bind('click', function() {
         $('#detailBox').hide();
     });
});

$(document).ready(function(){
  TestApp.start();
});

