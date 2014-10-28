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
    userList: "#userList"
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

TestApp.on("start", function() {
     var objs = ['deployment', 'image', 'networkTemplate', 'network', 'node', 'service', 'site', 'slice', 'sliver'];

     for (var index in objs) {
         name = objs[index];
         tr_template = '#test-' + name + '-listitem-template';
         table_template = '#test-' + name + '-list-template';
         collection_name = name + "s";
         region_name = name + "List";

         itemViewClass = Marionette.ItemView.extend({
             template: tr_template,
             tagName: 'tr',
             className: 'test-tablerow',
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
         xos[collection_name].startPolling();
     }
});

$(document).ready(function(){
  TestApp.start();
});

