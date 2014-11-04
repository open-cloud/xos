OBJS = ['deployment', 'image', 'networkTemplate', 'network', 'networkSliver', 'networkDeployment', 'node', 'service', 'site', 'slice', 'sliceDeployment', 'slicePrivilege', 'sliver', 'user', 'sliceRole', 'userDeployment'];
NAV_OBJS = ['deployment', 'site', 'slice', 'user'];

XOSAdminApp = new XOSApplication({logTableId: "#logTable"});

XOSAdminApp.addRegions({
    navigation: "#navigationPanel",

    detail: "#detail",
    linkedObjs1: "#linkedObjs1",
    linkedObjs2: "#linkedObjs2",
    linkedObjs3: "#linkedObjs3",
    linkedObjs4: "#linkedObjs4"
});

XOSAdminApp.navigateToModel = function(app, detailClass, detailNavLink, model) {
     XOSAdminApp.Router.navigate(detailNavLink + "/" + model.id, {trigger: true});
};

ICON_CLASSES = {home: "icon-home", deployments: "icon-deployment", sites: "icon-site", slices: "icon-slice", users: "icon-user"};

XOSAdminApp.updateNavigationPanel = function() {
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
     for (var index in OBJS) {
         name = OBJS[index];
         tr_template = '#xosAdmin-' + name + '-listitem-template';
         table_template = '#xosAdmin-' + name + '-list-template';
         detail_template = '#xosAdmin-' + name + '-detail-template';
         collection_name = name + "s";
         region_name = name + "List";
         detailNavLink = collection_name;

         detailClass = XOSDetailView.extend({
            template: detail_template,
            app: XOSAdminApp,
         });
         XOSAdminApp[collection_name + "DetailView"] = detailClass;

         itemViewClass = XOSItemView.extend({
             detailClass: detailClass,
             template: tr_template,
             app: XOSAdminApp,
             detailNavLink: detailNavLink,
         });

         listViewClass = XOSListView.extend({
             childView: itemViewClass,
             template: table_template,
             collection: xos[collection_name],
             title: name + "s",
             app: XOSAdminApp,
         });

         XOSAdminApp[collection_name + "ListView"] = listViewClass;

         xos[collection_name].fetch(); //startPolling();
     }
};

XOSAdminApp.initRouter = function() {
    router = Marionette.AppRouter.extend({
    });

    var api = {};
    var routes = {};

    for (var index in OBJS) {
        name = OBJS[index];
        collection_name = name + "s";
        nav_url = collection_name;
        api_command = "list" + collection_name.charAt(0).toUpperCase() + collection_name.slice(1);
        listViewName = collection_name + "ListView";
        detailViewName = collection_name + "DetailView";

        api[api_command] = XOSAdminApp.listViewShower(listViewName, "detail");
        routes[nav_url] = api_command;

        nav_url = collection_name + "/:id";
        api_command = "detail" + collection_name.charAt(0).toUpperCase() + collection_name.slice(1);

        api[api_command] = XOSAdminApp.detailShower(detailViewName, collection_name, "detail");
        routes[nav_url] = api_command;
    };

    XOSAdminApp.Router = new router({ appRoutes: routes, controller: api });
}

XOSAdminApp.on("start", function() {
     XOSAdminApp.buildViews();

     XOSAdminApp.initRouter();

     XOSAdminApp.updateNavigationPanel();

     if (Backbone.history) {
         console.log("history start");
         Backbone.history.start();
     }
});

$(document).ready(function(){
    XOSAdminApp.start();
});

