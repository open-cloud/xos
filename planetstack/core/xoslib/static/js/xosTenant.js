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
                     XOSTenantApp.addSlice();
                     },

            deleteClicked: function(e) {
                     XOSTenantApp.deleteSlice(this.options.linkedView.model);
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
    hideTabsByDefault: true,
    varName: "XOSTenantApp",
});

XOSTenantApp.addRegions({
    tenantSliceSelector: "#tenantSliceSelector",
    tenantSummary: "#tenantSummary",
    tenantSiteList: "#tenantSiteList",
    tenantButtons: "#tenantButtons",
    tenantAddSliceInterior: "#tenant-addslice-interior",
});

XOSTenantApp.buildViews = function() {
     XOSTenantApp.tenantSites = new XOSTenantSiteCollection();

     tenantSummaryClass = XOSDetailView.extend({template: "#xos-detail-template",
                                                app: XOSTenantApp,
                                                detailFields: ["serviceClass", "image_preference", "network_ports", "mount_data_sets"]});

     XOSTenantApp.tenantSummaryView = tenantSummaryClass;

     tenantAddClass = XOSDetailView.extend({template: "#xos-detail-template",
                                                app: XOSTenantApp,
                                                detailFields: ["name", "description"]});

     XOSTenantApp.tenantAddView = tenantAddClass;

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
             XOSTenantApp.navToSlice(id);
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

XOSTenantApp.navToSlice = function(id) {
    XOSTenantApp.viewSlice(xos.slicesPlus.get(id));
};

XOSTenantApp.adjustCollectionField = function(collectionName, id, fieldName, amount) {
    model = XOSTenantApp[collectionName].get(id);
    model.set(fieldName, Math.max(model.get(fieldName) + amount, 0));
};

XOSTenantApp.addSlice = function() {
    var app=this;
    model = new xos.slicesPlus.model({site: xos.tenant().current_user_site_id});
    console.log(model);
    var detailView = new XOSTenantApp.tenantAddView({model: model, collection: xos.slicesPlus});
    detailView.dialog = $("tenant-addslice-dialog");
    app.tenantAddSliceInterior.show(detailView);
    $("#tenant-addslice-dialog").dialog({
       autoOpen: false,
       modal: true,
       width: 640,
       buttons : {
            "Save" : function() {
              var addDialog = this;
              detailView.synchronous = true;
              detailView.afterSave = function() { $(addDialog).dialog("close"); XOSTenantApp.navToSlice(detailView.model.id); }
              detailView.save();
            },
            "Cancel" : function() {
              $(this).dialog("close");
            }
          }
        });
    $("#tenant-addslice-dialog").dialog("open");
};

XOSTenantApp.deleteSlice = function(model) {
    var app=this;
    app.deleteDialog(model, function() { console.log("afterDelete"); app.viewSlice(undefined); });
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

XOSTenantApp.startNavigation = function() {
    Backbone.history.start();
    XOSTenantApp.navigationStarted = true;
}

XOSTenantApp.collectionLoadChange = function() {
    stats = xos.getCollectionStatus();

    if (!XOSTenantApp.navigationStarted) {
        if (stats["isLoaded"] + stats["failedLoad"] >= stats["startedLoad"]) {
            XOSTenantApp.viewSlice(undefined);
        } else {
            $("#tenantSummary").html("<h3>Loading...</h3><div id='xos-startup-progress'></div>");
            $("#xos-startup-progress").progressbar({value: stats["completedLoad"], max: stats["startedLoad"]});
        }
    }
};

XOSTenantApp.on("start", function() {
     XOSTenantApp.buildViews();

     // fire it once to initially show the progress bar
     XOSTenantApp.collectionLoadChange();

     // fire it each time the collection load status is updated
     Backbone.on("xoslib:collectionLoadChange", XOSTenantApp.collectionLoadChange);
});

$(document).ready(function(){
    XOSTenantApp.start();
});

