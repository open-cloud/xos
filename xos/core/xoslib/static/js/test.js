/* eslint-disable */
TestApp = new XOSApplication();

TestApp.addRegions({
    deploymentList: "#deploymentList",
    imageList: "#imageList",
    networkTemplateList: "#networkTemplateList",
    networkList: "#networkList",
    nodeList: "#nodeList",
    serviceList: "#serviceList",
    siteList: "#siteList",
    sliceList: "#sliceList",
    instanceList: "#instanceList",
    userList: "#userList",
    detail: "#detail",
    linkedObjs1: "#linkedObjs1",
    linkedObjs2: "#linkedObjs2",
    linkedObjs3: "#linkedObjs3",
    linkedObjs4: "#linkedObjs4"
});

//TestApp.navigateToDetail = function(detailView) {
//     $(TestApp.detailBoxId).show();
//     TestApp.detail.show(detailView);
//};

TestApp.navigateToModel = function(app, detailClass, detailNavLink, model) {

    var detailView = new detailClass({
        model: model,
    });

    $(app.detailBoxId).show();
    app.detail.show(detailView);
    detailView.showLinkedItems();
};

TestApp.on("start", function() {
     var objs = ['deployment', 'image', 'networkTemplate', 'network', 'port', 'networkDeployment', 'node', 'service', 'site', 'slice', 'sliceDeployment', 'slicePrivilege', 'instance', 'user', 'sliceRole', 'userDeployment'];

     for (var index in objs) {
         name = objs[index];
         tr_template = '#xosAdmin-' + name + '-listitem-template';
         table_template = '#xosAdmin-' + name + '-list-template';
         detail_template = '#xosAdmin-' + name + '-detail-template';
         collection_name = name + "s";
         region_name = name + "List";

         detailClass = XOSDetailView.extend({
            template: detail_template,
            app: TestApp,
         });

         itemViewClass = XOSItemView.extend({
             detailClass: detailClass,
             template: tr_template,
             app: TestApp,
         });

         listViewClass = XOSListView.extend({
             childView: itemViewClass,
             template: table_template,
             collection: xos[collection_name],
             title: name + "s",
             app: TestApp,
         });
         TestApp[collection_name + "ListView"] = listViewClass;

         var listView = new listViewClass();

         if (region_name in TestApp.getRegions()) {
             TestApp[region_name].show(listView);
         }
         xos[collection_name].fetch(); //startPolling();
     }

     $('#close-detail-view').unbind().bind('click', function() {
         $('#detailBox').hide();
     });
});

$(document).ready(function(){
    TestApp.start();
});
/* eslint-enable */
