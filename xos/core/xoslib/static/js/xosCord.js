/* eslint-disable */
OBJS = ['cordSubscriber', 'cordUser'];

CordAdminApp = new XOSApplication({
    logTableId: "#logTable",
    statusMsgId: "#statusMsg",
    hideTabsByDefault: true
});

CordAdminApp.addRegions({
    navigation: "#navigationPanel",

    detail: "#detail",
    linkedObjs1: "#linkedObjs1",
    linkedObjs2: "#linkedObjs2",
    linkedObjs3: "#linkedObjs3",
    linkedObjs4: "#linkedObjs4",

    addChildDetail: "#xos-addchild-detail",

    rightButtonPanel: "#rightButtonPanel"
});

CordAdminApp.navigate = function(what, modelName, modelId) {
    collection_name = modelName + "s";
    if (what=="list") {
        CordAdminApp.Router.navigate(collection_name, {trigger: true})
    } else if (what=="detail") {
        CordAdminApp.Router.navigate(collection_name + "/" + modelId, {trigger: true})
    } else if (what=="add") {
        CordAdminApp.Router.navigate("add" + firstCharUpper(modelName), {trigger: true, force: true})
    }
}

CordAdminApp.buildViews = function() {
     genericAddChildClass = XOSDetailView.extend({template: "#xos-add-template",
                                                        app: CordAdminApp});
     CordAdminApp["genericAddChildView"] = genericAddChildClass;

     genericDetailClass = XOSDetailView.extend({template: "#xos-detail-template",
                                                           app: CordAdminApp});
     CordAdminApp["genericDetailView"] = genericDetailClass;

     genericItemViewClass = XOSItemView.extend({template: "#xos-listitem-template",
                                                app: CordAdminApp});
     CordAdminApp["genericItemView"] = genericItemViewClass;

     //genericListViewClass = XOSListView.extend({template: "#xos-list-template",
     //                                           app: CordAdminApp});

     genericListViewClass = XOSDataTableView.extend({template: "#xos-list-template", app: CordAdminApp});
     CordAdminApp["genericListView"] = genericListViewClass;

     for (var index in OBJS) {
         name = OBJS[index];
         tr_template = '#xosAdmin-' + name + '-listitem-template';
         table_template = '#xosAdmin-' + name + '-list-template';
         detail_template = '#xosAdmin-' + name + '-detail-template';
         add_child_template = '#xosAdmin-' + name + '-add-child-template';
         collection_name = name + "s";
         region_name = name + "List";
         templates = {cordSubscriber: "#xos-cord-subscriber-template"};

         if (window["XOSDetailView_" + name]) {
             detailClass = window["XOSDetailView_" + name].extend( {template: templates[name] || "#xos-detail-template",
                                                                    app: CordAdminApp});
         } else {
             detailClass = genericDetailClass.extend( {template: templates[name] || "#xos-detail-template", });
         }
         if ($(detail_template).length) {
             detailClass = detailClass.extend({
                template: detail_template,
             });
         }
         CordAdminApp[collection_name + "DetailView"] = detailClass;

         if (window["XOSDetailView_" + name]) {
             addClass = window["XOSDetailView_" + name].extend({template: "#xos-add-template",
                                                                    app: CordAdminApp});
         } else {
             addClass = genericAddChildClass;
         }
         if ($(add_child_template).length) {
             addClass = detailClass.extend({
                template: add_child_template,
             });
         }
         CordAdminApp[collection_name + "AddChildView"] = addClass;

         if ($(tr_template).length) {
             itemViewClass = XOSItemView.extend({
                 template: tr_template,
                 app: CordAdminApp,
             });
         } else {
             itemViewClass = genericItemViewClass;
         }

         if ($(table_template).length) {
             listViewClass = XOSListView.extend({
                 childView: itemViewClass,
                 template: table_template,
                 collection: xos[collection_name],
                 title: name + "s",
                 app: CordAdminApp,
             });
         } else {
             listViewClass = genericListViewClass.extend( { childView: itemViewClass,
                                                            collection: xos[collection_name],
                                                            title: name + "s",
                                                           } );
         }

         CordAdminApp[collection_name + "ListView"] = listViewClass;

         xos[collection_name].fetch(); //startPolling();
     }
};

CordAdminApp.initRouter = function() {
    router = XOSRouter;
    var api = {};
    var routes = {};

    for (var index in OBJS) {
        name = OBJS[index];
        collection_name = name + "s";
        nav_url = collection_name;
        api_command = "list" + firstCharUpper(collection_name);
        listViewName = collection_name + "ListView";
        detailViewName = collection_name + "DetailView";
        addChildViewName = collection_name + "AddChildView";

        api[api_command] = CordAdminApp.createListHandler(listViewName, collection_name, "detail", collection_name);
        routes[nav_url] = api_command;

        nav_url = collection_name + "/:id";
        api_command = "detail" + firstCharUpper(collection_name);

        api[api_command] = CordAdminApp.createDetailHandler(detailViewName, collection_name, "detail", name);
        routes[nav_url] = api_command;

        nav_url = "add" + firstCharUpper(name);
        api_command = "add" + firstCharUpper(name);
        api[api_command] = CordAdminApp.createAddHandler(detailViewName, collection_name, "detail", name);
        routes[nav_url] = api_command;

        nav_url = "addChild" + firstCharUpper(name) + "/:parentModel/:parentField/:parentId";
        api_command = "addChild" + firstCharUpper(name);
        api[api_command] = CordAdminApp.createAddChildHandler(addChildViewName, collection_name);
        routes[nav_url] = api_command;

        nav_url = "delete" + firstCharUpper(name) + "/:id";
        api_command = "delete" + firstCharUpper(name);
        api[api_command] = CordAdminApp.createDeleteHandler(collection_name, name);
        routes[nav_url] = api_command;
    };

    routes["*part"] = "listCordSubscribers";

    CordAdminApp.Router = new router({ appRoutes: routes, controller: api });
};

CordAdminApp.startNavigation = function() {
    Backbone.history.start();
    CordAdminApp.navigationStarted = true;
}

CordAdminApp.collectionLoadChange = function() {
    stats = xos.getCollectionStatus();

    if (!CordAdminApp.navigationStarted) {
        if (stats["isLoaded"] + stats["failedLoad"] >= stats["startedLoad"]) {
            CordAdminApp.startNavigation();
        } else {
            $("#detail").html("<h3>Loading...</h3><div id='xos-startup-progress'></div>");
            $("#xos-startup-progress").progressbar({value: stats["completedLoad"], max: stats["startedLoad"]});
        }
    }
};

CordAdminApp.on("start", function() {
     CordAdminApp.buildViews();

     CordAdminApp.initRouter();

     // fire it once to initially show the progress bar
     CordAdminApp.collectionLoadChange();

     // fire it each time the collection load status is updated
     Backbone.on("xoslib:collectionLoadChange", CordAdminApp.collectionLoadChange);
});

$(document).ready(function(){
    CordAdminApp.start();
});
/* eslint-enable */
