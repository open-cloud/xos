XOSTenantSite = XOSModel.extend( {
    listFields: ["name", "allocated"],
    modelName: "tenantSite",
    collectionName: "tenantSites"
});

XOSTenantSiteCollection = XOSCollection.extend( {
    listFields: ["name", "allocated"],
    modelName: "tenantSite",
    collectionName: "tenantSites",

    updateFromSlice: function(slice) {
        var tenantSites = [];
        var id = 0;
        for (siteName in slice.attributes.site_allocation) {
            allocated = slice.attributes.site_allocation[siteName];
            tenantSites.push(new XOSTenantSite( { name: siteName, allocated: allocated, id: id} ));
            id = id + 1;
        }
        for (index in xos.tenantview.models[0].attributes.blessed_site_names) {
            siteName = xos.tenantview.models[0].attributes.blessed_site_names[index];
            if (! (siteName in slice.attributes.site_allocation)) {
                tenantSites.push(new XOSTenantSite( { name: siteName, allocated: 0, id: id} ));
                id = id + 1;
            }
        }
        this.set(tenantSites);
    },
});

XOSTenantButtonView = Marionette.ItemView.extend({
            template: "#xos-tenant-buttons-template",

            events: {"click button.btn-tenant-create": "createClicked",
                     "click button.btn-tenant-delete": "deleteClicked",
                     "click button.btn-tenant-add-user": "addUserClicked",
                     "click button.btn-tenant-save": "saveClicked",
                     },

            createClicked: function(e) {
                     },

            deleteClicked: function(e) {
                     this.options.linkedView.deleteClicked.call(this.options.linkedView, e);
                     },

            addUserClicked: function(e) {
                     },

            saveClicked: function(e) {
                     this.options.linkedView.submitContinueClicked.call(this.options.linkedView, e);
                     },
            });

XOSTenantApp = new XOSApplication({
    logTableId: "#logTable",
    statusMsgId: "#statusMsg",
    hideTabsByDefault: true
});

XOSTenantApp.addRegions({
    tenantSliceSelector: "#tenantSliceSelector",
    tenantSummary: "#tenantSummary",
    tenantSiteList: "#tenantSiteList",
    tenantButtons: "#tenantButtons",
});

XOSTenantApp.buildViews = function() {
     XOSTenantApp.tenantSites = new XOSTenantSiteCollection();

     tenantSummaryClass = XOSDetailView.extend({template: "#xos-detail-template",
                                                app: XOSTenantApp,
                                                detailFields: ["serviceClass", "image_preference", "network_ports", "mount_data_sets"]});

     XOSTenantApp.tenantSummaryView = tenantSummaryClass;

     tenantSiteItemClass = XOSItemView.extend({template: "#xos-listitem-template",
                                               app: XOSTenantApp});

     XOSTenantApp.tenantSiteItemView = tenantSiteItemClass;

     tenantSiteListClass = XOSDataTableView.extend({template: "#xos-list-template",
                                               app: XOSTenantApp,
                                               childView: tenantSiteItemClass,
                                               collection: XOSTenantApp.tenantSites,
                                               title: "sites",
                                               inputType: {allocated: "spinner"},
                                               noDeleteColumn: true,
                                               });

     XOSTenantApp.tenantSiteListView = tenantSiteListClass;

     XOSTenantApp.tenantSliceSelectorView = SliceSelectorView.extend( {
         sliceChanged: function(id) {
             //console.log("navigate to " + id);
             XOSTenantApp.Router.navigate("slice/" + id, {trigger: true});
         },
     });

     xos.sites.fetch();
     xos.slicesPlus.fetch();
     xos.tenantview.fetch();
};

make_choices = function(list_of_names, list_of_values) {
    result = [];
    if (!list_of_values) {
        for (index in list_of_names) {
            displayName = list_of_names[index];
            result.push( [displayName, displayName] );
        }
    }
    return result;
};

XOSTenantApp.viewSlice = function(model) {
    if (!model && xos.slicesPlus.models.length > 0) {
        model = xos.slicesPlus.models[0];
    }

    sliceSelector = new XOSTenantApp.tenantSliceSelectorView({collection: xos.slicesPlus,
                                                              selectedID: model.id,
                                                             } );
    XOSTenantApp.sliceSelector = sliceSelector;
    XOSTenantApp.tenantSliceSelector.show(sliceSelector);

    tenantSummary = new XOSTenantApp.tenantSummaryView({model: model,
                                                        choices: {mount_data_sets: make_choices(xos.tenantview.models[0].attributes.public_volume_names, null),
                                                                  image_preference: make_choices(xos.tenantview.models[0].attributes.blessed_image_names, null)},
                                                       });
    XOSTenantApp.tenantSummary.show(tenantSummary);

    tenantSites = new XOSTenantSiteCollection();
    tenantSites.updateFromSlice(model);
    XOSTenantApp.tenantSites = tenantSites;

    tenantSiteList = new XOSTenantApp.tenantSiteListView({collection: tenantSites });
    XOSTenantApp.tenantSiteList.show(tenantSiteList);
    // on xos.slicePlus.sort, need to update xostenantapp.tenantSites

    XOSTenantApp.tenantButtons.show( new XOSTenantButtonView( { app: XOSTenantApp,
                                                                linkedView: tenantSummary } ) );
};

XOSTenantApp.initRouter = function() {
    router = XOSRouter;
    var api = {};
    var routes = {};

    nav_url = "slice/:id";
    api_command = "viewSlice";
    api[api_command] = function(id) { XOSTenantApp.viewSlice(xos.slicesPlus.get(id)); };
    routes[nav_url] = api_command;

    nav_url = "increase/:collectionName/:id/:fieldName";
    api_command = "increase";
    api[api_command] = function(collectionName, id, fieldName) {
                           XOSTenantApp.Router.showPreviousURL();
                           model = XOSTenantApp[collectionName].get(id);
                           model.set(fieldName, model.get(fieldName) + 1);
                       };
    routes[nav_url] = api_command;

    nav_url = "decrease/:collectionName/:id/:fieldName";
    api_command = "decrease";
    api[api_command] = function(collectionName, id, fieldName) {
                           XOSTenantApp.Router.showPreviousURL();
                           model = XOSTenantApp[collectionName].get(id);
                           model.set(fieldName, Math.max(0, model.get(fieldName) - 1));
                       };
    routes[nav_url] = api_command;

    nav_url = "*path";
    api_command = "defaultRoute";
    api[api_command] = function() { XOSTenantApp.viewSlice(undefined); };
    routes[nav_url] = api_command;

    XOSTenantApp.Router = new router({ appRoutes: routes, controller: api });
};

XOSTenantApp.startNavigation = function() {
    Backbone.history.start();
    XOSTenantApp.navigationStarted = true;
}

XOSTenantApp.collectionLoadChange = function() {
    stats = xos.getCollectionStatus();

    if (!XOSTenantApp.navigationStarted) {
        if (stats["isLoaded"] + stats["failedLoad"] >= stats["startedLoad"]) {
            XOSTenantApp.startNavigation();

            //if (xos.slicesPlus.models.length > 0) {
            //    XOSTenantApp.Router.navigate("slice/" + xos.slicesPlus.models[0].id, {trigger:true});
            //}
        } else {
            $("#tenantSummary").html("<h3>Loading...</h3><div id='xos-startup-progress'></div>");
            $("#xos-startup-progress").progressbar({value: stats["completedLoad"], max: stats["startedLoad"]});
        }
    }
};

XOSTenantApp.on("start", function() {
     XOSTenantApp.buildViews();

     XOSTenantApp.initRouter();

     // fire it once to initially show the progress bar
     XOSTenantApp.collectionLoadChange();

     // fire it each time the collection load status is updated
     Backbone.on("xoslib:collectionLoadChange", XOSTenantApp.collectionLoadChange);
});

$(document).ready(function(){
    XOSTenantApp.start();
});

