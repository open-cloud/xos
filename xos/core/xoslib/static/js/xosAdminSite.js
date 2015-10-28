/* eslint-disable */
OBJS = ['deployment', 'image', 'networkTemplate', 'network', 'port',
        'node', 'service', 'site', 'slice',  'slicePrivilege', 'instance',
        'user', 'sliceRole',  'flavor', 'controller', 'siteDeployment',
        'controller_image', 'controller_network', 'controller_slice', 'controller_user'];
NAV_OBJS = ['deployment', 'site', 'slice', 'user'];

REWRITES = {"/admin/core/deployment/": "#deployments",
            "/admin/core/site/" : "#sites",
            "/admin/core/slice/" : "#slices",
            "/admin/core/user/" : "#users"};

XOSAdminApp = new XOSApplication({
    logTableId: "#logTable",
    statusMsgId: "#statusMsg",
    hideTabsByDefault: true
});

XOSAdminApp.addRegions({
    navigation: "#navigationPanel",

    detail: "#detail",
    linkedObjs1: "#linkedObjs1",
    linkedObjs2: "#linkedObjs2",
    linkedObjs3: "#linkedObjs3",
    linkedObjs4: "#linkedObjs4",

    addChildDetail: "#xos-addchild-detail",

    rightButtonPanel: "#rightButtonPanel"
});

XOSAdminApp.navigate = function(what, modelName, modelId) {
    console.log("XOSAsminApp.navigate");
    collection_name = modelName + "s";
    if (what=="list") {
        XOSAdminApp.Router.navigate(collection_name, {trigger: true})
    } else if (what=="detail") {
        XOSAdminApp.Router.navigate(collection_name + "/" + modelId, {trigger: true})
    } else if (what=="add") {
        XOSAdminApp.Router.navigate("add" + firstCharUpper(modelName), {trigger: true, force: true})
    }
}

ICON_CLASSES = {home: "icon-home", deployments: "icon-deployment", sites: "icon-site", slices: "icon-slice", users: "icon-user"};

XOSAdminApp.updateNavigationPanel = function() {
    console.log('UPDATE NAV!!!');
    buttonTemplate=$("#xos-navbutton").html();
    assert(buttonTemplate != undefined, "buttonTemplate is undefined");
    html="<div class='left-nav'><ul>";
    for (var index in NAV_OBJS) {
        name = NAV_OBJS[index];
        collection_name = name+"s";
        nav_url = "#" + collection_name;
        id = "nav-"+name;
        icon_class = ICON_CLASSES[collection_name] || "icon-cog";

        html = html + _.template(buttonTemplate, {name: collection_name, router: "XOSAdminApp.Router", routeUrl: nav_url, iconClass: icon_class});
    }

    html = html + "</ul>";

    $("#navigationPanel").html(html);
};

XOSAdminApp.buildViews = function() {
     genericAddChildClass = XOSDetailView.extend({template: "#xos-add-template",
                                                        app: XOSAdminApp});
     XOSAdminApp["genericAddChildView"] = genericAddChildClass;

     genericDetailClass = XOSDetailView.extend({template: "#xos-detail-template",
                                                           app: XOSAdminApp});
     XOSAdminApp["genericDetailView"] = genericDetailClass;

     genericItemViewClass = XOSItemView.extend({template: "#xos-listitem-template",
                                                app: XOSAdminApp});
     XOSAdminApp["genericItemView"] = genericItemViewClass;

     //genericListViewClass = XOSListView.extend({template: "#xos-list-template",
     //                                           app: XOSAdminApp});

     genericListViewClass = XOSDataTableView.extend({template: "#xos-list-template", app: XOSAdminApp});
     XOSAdminApp["genericListView"] = genericListViewClass;

     for (var index in OBJS) {
         name = OBJS[index];
         tr_template = '#xosAdmin-' + name + '-listitem-template';
         table_template = '#xosAdmin-' + name + '-list-template';
         detail_template = '#xosAdmin-' + name + '-detail-template';
         add_child_template = '#xosAdmin-' + name + '-add-child-template';
         collection_name = name + "s";
         region_name = name + "List";

         if (window["XOSDetailView_" + name]) {
             detailClass = window["XOSDetailView_" + name].extend({template: "#xos-detail-template",
                                                                    app: XOSAdminApp});
         } else {
             detailClass = genericDetailClass;
         }
         if ($(detail_template).length) {
             detailClass = detailClass.extend({
                template: detail_template,
             });
         }
         XOSAdminApp[collection_name + "DetailView"] = detailClass;

         if (window["XOSDetailView_" + name]) {
             addClass = window["XOSDetailView_" + name].extend({template: "#xos-add-template",
                                                                    app: XOSAdminApp});
         } else {
             addClass = genericAddChildClass;
         }
         if ($(add_child_template).length) {
             addClass = detailClass.extend({
                template: add_child_template,
             });
         }
         XOSAdminApp[collection_name + "AddChildView"] = addClass;

         if ($(tr_template).length) {
             itemViewClass = XOSItemView.extend({
                 template: tr_template,
                 app: XOSAdminApp,
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
                 app: XOSAdminApp,
             });
         } else {
             listViewClass = genericListViewClass.extend( { childView: itemViewClass,
                                                            collection: xos[collection_name],
                                                            title: name + "s",
                                                           } );
         }

         XOSAdminApp[collection_name + "ListView"] = listViewClass;

         xos[collection_name].fetch(); //startPolling();
     }
};

XOSAdminApp.initRouter = function() {
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

        api[api_command] = XOSAdminApp.createListHandler(listViewName, collection_name, "detail", collection_name);
        routes[nav_url] = api_command;

        nav_url = collection_name + "/:id";
        api_command = "detail" + firstCharUpper(collection_name);

        api[api_command] = XOSAdminApp.createDetailHandler(detailViewName, collection_name, "detail", name);
        routes[nav_url] = api_command;

        nav_url = "add" + firstCharUpper(name);
        api_command = "add" + firstCharUpper(name);
        api[api_command] = XOSAdminApp.createAddHandler(detailViewName, collection_name, "detail", name);
        routes[nav_url] = api_command;

        nav_url = "addChild" + firstCharUpper(name) + "/:parentModel/:parentField/:parentId";
        api_command = "addChild" + firstCharUpper(name);
        api[api_command] = XOSAdminApp.createAddChildHandler(addChildViewName, collection_name);
        routes[nav_url] = api_command;

        nav_url = "delete" + firstCharUpper(name) + "/:id";
        api_command = "delete" + firstCharUpper(name);
        api[api_command] = XOSAdminApp.createDeleteHandler(collection_name, name);
        routes[nav_url] = api_command;
    };

    routes["*part"] = "listSlices";

    XOSAdminApp.Router = new router({ appRoutes: routes, controller: api });
};

/* rewriteLinks

   Rewrite the links in the suit navbar from django-links to marionette
   links. This let's us intercept the navbar and make it function within
   this view rather than jumping back out to a django view.
*/

XOSAdminApp.rewriteLinks = function () {
    $("a").each(function() {
        href=$(this).attr("href");
        rewrite_href=REWRITES[href];
        if (rewrite_href) {
            $(this).attr("href", rewrite_href);
        }
    });
};

XOSAdminApp.startNavigation = function() {
    Backbone.history.start();
    XOSAdminApp.navigationStarted = true;
}

XOSAdminApp.collectionLoadChange = function() {
    stats = xos.getCollectionStatus();

    if (!XOSAdminApp.navigationStarted) {
        if (stats["isLoaded"] + stats["failedLoad"] >= stats["startedLoad"]) {
            XOSAdminApp.startNavigation();
        } else {
            $("#detail").html("<h3>Loading...</h3><div id='xos-startup-progress'></div>");
            $("#xos-startup-progress").progressbar({value: stats["completedLoad"], max: stats["startedLoad"]});
        }
    }
};

XOSAdminApp.on("start", function() {
     XOSAdminApp.buildViews();

     XOSAdminApp.initRouter();

     XOSAdminApp.updateNavigationPanel();

     XOSAdminApp.rewriteLinks();

     // fire it once to initially show the progress bar
     XOSAdminApp.collectionLoadChange();

     // fire it each time the collection load status is updated
     Backbone.on("xoslib:collectionLoadChange", XOSAdminApp.collectionLoadChange);
});

$(document).ready(function(){
    XOSAdminApp.start();
});
/* eslint-enable */
