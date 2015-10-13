/* eslint-disable */

XOSTenantSite = XOSModel.extend( {
    listFields: ["name", "allocated"],
    modelName: "tenantSite",
    collectionName: "tenantSites"
});

XOSTenantSiteCollection = XOSCollection.extend( {
    listFields: ["name", "allocated", "ready"],
    modelName: "tenantSite",
    collectionName: "tenantSites",

    getFromSlice: function(slice) {
        var tenantSites = [];
        var id = 0;
        for (siteName in slice.attributes.site_allocation) {
            allocated = slice.attributes.site_allocation[siteName];
            ready = slice.attributes.site_ready[siteName] || 0;
            tenantSites.push(new XOSTenantSite( { name: siteName, allocated: allocated, ready: ready, id: id} ));
            id = id + 1;
        }
        for (index in xos.tenantview.models[0].attributes.blessed_site_names) {
            siteName = xos.tenantview.models[0].attributes.blessed_site_names[index];
            if (! (siteName in slice.attributes.site_allocation)) {
                tenantSites.push(new XOSTenantSite( { name: siteName, allocated: 0, ready: 0, id: id} ));
                id = id + 1;
            }
        }
        this.set(tenantSites);

        var that=this;
        this.listenTo(slice, 'change', function() { that.getReadyFromSlice(slice); })
    },

    getReadyFromSlice: function(slice) {
        for (siteName in slice.attributes.site_ready) {
            ready = slice.attributes.site_ready[siteName];
            for (index in this.models) {
                tenantSite = this.models[index];
                if (tenantSite.attributes.name == siteName) {
                    tenantSite.set("ready", ready);
                }
            }
        }
    },

    putToSlice: function(slice) {
        slice.attributes.site_allocation = {};
        for (index in this.models) {
            var model = this.models[index];
            slice.attributes.site_allocation[ model.attributes.name ] = model.attributes.allocated;
        }
    },
});

XOSEditUsersView = Marionette.ItemView.extend({
            template: "#tenant-edit-users",
            viewInitializers: [],

            onShow: function() {
                _.each(this.viewInitializers, function(initializer) {
                    initializer();
                });
            },

            templateHelpers: function() { return { detailView: this, model: this.model }; },

            });

XOSTenantSummaryView = XOSDetailView.extend({
            events: {"change": "onChange"},

            onChange: function(e) {
                XOSTenantApp.setDirty(true);
            },

            saveSuccess: function() {
                console.log("saveSuccess!");
                XOSTenantApp.setDirty(false);
            },

            });


XOSTenantButtonView = Marionette.ItemView.extend({
            template: "#xos-tenant-buttons-template",

            events: {"click button.btn-tenant-create": "createClicked",
                     "click button.btn-tenant-delete": "deleteClicked",
                     "click button.btn-tenant-add-user": "addUserClicked",
                     "click button.btn-tenant-save": "saveClicked",
                     "click button.btn-tenant-download-ssh": "downloadClicked",
                     },

            createClicked: function(e) {
                     XOSTenantApp.addSlice();
                     },

            deleteClicked: function(e) {
                     XOSTenantApp.deleteSlice(this.options.linkedView.model);
                     },

            addUserClicked: function(e) {
                     XOSTenantApp.editUsers(this.options.linkedView.model);
                     },

            downloadClicked: function(e) {
                     XOSTenantApp.downloadSSH(this.options.linkedView.model);
                     },

            saveClicked: function(e) {
                     model = this.options.linkedView.model;
                     model.tenantSiteCollection.putToSlice(model);
                     model.attributes.users = model.usersBuffer;

                     e.preventDefault();
                     this.options.linkedView.save();
                     //this.options.linkedView.submitContinueClicked.call(this.options.linkedView, e);
                     //XOSTenantApp.setDirty(false);
                     },
            });

XOSTenantApp = new XOSApplication({
    logTableId: "#logTable",
    statusMsgId: "#statusMsg",
    hideTabsByDefault: true,
    dirty: false,
    varName: "XOSTenantApp",
});

XOSTenantApp.addRegions({
    tenantSliceSelector: "#tenantSliceSelector",
    tenantSummary: "#tenantSummary",
    tenantSiteList: "#tenantSiteList",
    tenantButtons: "#tenantButtons",
    tenantAddSliceInterior: "#tenant-addslice-interior",
    tenantEditUsersInterior: "#tenant-edit-users-interior",
    tenantSSHCommandsInterior: "#tenant-ssh-commands-interior",
});

XOSTenantApp.setDirty = function(dirty) {
    XOSTenantApp.dirty = dirty;
    if (dirty) {
        $("button.btn-tenant-save").addClass("btn-success");
    } else {
        $("button.btn-tenant-save").removeClass("btn-success");
    }
};

XOSTenantApp.buildViews = function() {
     XOSTenantApp.tenantSites = new XOSTenantSiteCollection();

     tenantSummaryClass = XOSTenantSummaryView.extend({template: "#xos-detail-template",
                                                app: XOSTenantApp,
                                                detailFields: ["serviceClass", "default_image", "default_flavor", "network_ports"],
                                                fieldDisplayNames: {serviceClass: "Service Level", "default_flavor": "Flavor", "default_image": "Image", "mount_data_sets": "Data Sets"},
                                                helpText: {"serviceClass": "Existing instances will be re-instantiated if changed",
                                                           "default_image": "Existing instances will be re-instantiated if changed",
                                                           "default_flavor": "Existing instances will be re-instantiated if changed"},

                                                onShow: function() {
                                                    // the slice selector is in a different table, so make every label cell the maximal width
                                                    make_same_width("#xos-tenant-view-panel", ".xos-label-cell");
                                                },
                                                });

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
                                               disablePaginate: true,
                                               disableFilter: true,
                                               fieldDisplayNames: {"name": "Site"},
                                               });

     XOSTenantApp.tenantSiteListView = tenantSiteListClass;

     XOSTenantApp.tenantSliceSelectorView = SliceSelectorView.extend( {
         sliceChanged: function(id) {
             XOSTenantApp.navToSlice(id);
         },
         filter: function(slice) {
             return slice.attributes.current_user_can_see;
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
    } else {
        for (index in list_of_names) {
            displayName = list_of_names[index];
            id = list_of_values[index];
            result.push( [displayName, id] );
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
    XOSTenantApp.setDirty(true);
};

XOSTenantApp.addSlice = function() {
    var app=this;

    if (!xos.tenant().current_user_can_create_slice) {
        window.alert("You do not have sufficient rights to create a slice on your site");
        return;
    }

    model = new xos.slicesPlus.model({site: xos.tenant().current_user_site_id,
                                      name: xos.tenant().current_user_login_base + "_",
                                      creator: xos.tenant().current_user_id});
    console.log(model);
    var detailView = new XOSTenantApp.tenantAddView({model: model,
                                                     collection: xos.slicesPlus,
                                                     noSubmitButton: true,
                                                    });
    detailView.dialog = $("#tenant-addslice-dialog");
    app.tenantAddSliceInterior.show(detailView);
    $("#tenant-addslice-dialog").dialog({
       autoOpen: false,
       modal: true,
       width: 640,
       buttons : {
            "Create Slice" : function() {
              var addDialog = this;
              console.log("SAVE!!!");
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

XOSTenantApp.editUsers = function(model) {
    var app=this;
    var detailView = new XOSEditUsersView({model: model, collection: xos.slicesPlus});
    detailView.dialog = $("#tenant-edit-users-dialog");
    app.tenantEditUsersInterior.show(detailView);
    $("#tenant-edit-users-dialog").dialog({
       autoOpen: false,
       modal: true,
       width: 640,
       buttons : {
            "Ok" : function() {
              var editDialog = this;
              user_ids = all_options($("#tenant-edit-users-dialog").find(".select-picker-to"));
              user_ids = user_ids.map( function(x) { return parseInt(x,10); } );
              if (!array_same_elements(user_ids, model.usersBuffer)) {
                  XOSTenantApp.setDirty(true);
              }
              model.usersBuffer = user_ids;
              $(editDialog).dialog("close");
            },
            "Cancel" : function() {
              $(this).dialog("close");
            }
          }
        });
    $("#tenant-edit-users-dialog").dialog("open");
};

XOSTenantApp.downloadSSH = function(model) {
    var sshCommands = "";
    for (index in model.attributes.sliceInfo.sshCommands) {
         sshCommand = model.attributes.sliceInfo.sshCommands[index];
         sshCommands = sshCommands + sshCommand + "\n";
    }

    if (sshCommands.length == 0) {
         alert("this slice has no instantiated instances yet");
         return;
    }

    var htmlView = new HTMLView({html: '<pre style="overflow: auto; word-wrap: normal; white-space: pre; word-wrap: normal;">' + sshCommands + '</pre>'});
    XOSTenantApp.tenantSSHCommandsInterior.show(htmlView);

    $("#tenant-ssh-commands-dialog").dialog({
       autoOpen: false,
       modal: true,
       width: 640,
       buttons : {
            "Download": function() {
                var dlLink = document.createElement('a');
                dlLink.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(sshCommands));
                dlLink.setAttribute('download', 'sshcommands.txt');
                dlLink.click();

                //window.open('data:text/text,' + encodeURIComponent(sshCommands));
            },
            "Close" : function() {
              $(this).dialog("close");
            },
          }
        });
    $("#tenant-ssh-commands-dialog").dialog("open");
};

XOSTenantApp.deleteSlice = function(model) {
    var app=this;
    app.deleteDialog(model, function() { console.log("afterDelete"); app.viewSlice(undefined); });
};

XOSTenantApp.viewSlice = function(model) {
    if (XOSTenantApp.dirty) {
        if (!confirm("The current instance has unsaved data -- view new instance anyway ?")) {
            $("#tenantSliceSelector select").val(XOSTenantApp.currentSlice.id);
            return;
        }
    }

    XOSTenantApp.setDirty(false);

    if (!model && xos.slicesPlus.models.length > 0) {
        model = xos.slicesPlus.models[0];
    }

    if (model) {
        sliceSelector = new XOSTenantApp.tenantSliceSelectorView({collection: xos.slicesPlus,
                                                                  selectedID: model ? model.id : null,
                                                                 } );
        XOSTenantApp.sliceSelector = sliceSelector;
        XOSTenantApp.tenantSliceSelector.show(sliceSelector);

        tenantSummary = new XOSTenantApp.tenantSummaryView({model: model,
                                                            choices: {mount_data_sets: make_choices(xos.tenant().public_volume_names, null),
                                                                      serviceClass: make_choices(xos.tenant().blessed_service_class_names, xos.tenant().blessed_service_classes),
                                                                      default_image: make_choices(xos.tenant().blessed_image_names, xos.tenant().blessed_images),
                                                                      default_flavor: make_choices(xos.tenant().blessed_flavor_names, xos.tenant().blessed_flavors),},
                                                           });
        XOSTenantApp.tenantSummary.show(tenantSummary);

        tenantSites = new XOSTenantSiteCollection();
        tenantSites.getFromSlice(model);
        model.usersBuffer = model.attributes.users; /* save a copy of 'users' that we can edit. This prevents another view (developer) from overwriting our copy with a fetch from the server */
        model.usersOrig = model.attributes.users;   /* save an immutable copy that we'll use for username lookups */
        model.user_namesOrig = model.attributes.user_names;
        model.tenantSiteCollection = tenantSites;
        XOSTenantApp.tenantSites = tenantSites;

        tenantSiteList = new XOSTenantApp.tenantSiteListView({collection: tenantSites });
        XOSTenantApp.tenantSiteList.show(tenantSiteList);
        // on xos.slicePlus.sort, need to update xostenantapp.tenantSites

        XOSTenantApp.tenantButtons.show( new XOSTenantButtonView( { app: XOSTenantApp,
                                                                    linkedView: tenantSummary } ) );

        XOSTenantApp.currentSlice = model;
    } else {
        XOSTenantApp.tenantSliceSelector.show(new HTMLView({html: ""}));
        XOSTenantApp.tenantSummary.show(new HTMLView({html: "You have no slices"}));
        XOSTenantApp.tenantSiteList.show(new HTMLView({html: ""}));
        XOSTenantApp.tenantButtons.show( new XOSTenantButtonView( { template: "#xos-tenant-buttons-noslice-template",
                                                                    app: XOSTenantApp,
                                                                    linkedView: tenantSummary } ) );
    }
};

XOSTenantApp.sanityCheck = function() {
    errors = [];
    if (xos.tenant().blessed_deployments && xos.tenant().blessed_deployments.length == 0) {
        errors.push("no blessed deployments");
    }
    if (xos.tenant().blessed_service_classes.length == 0) {
        errors.push("no blessed service classes");
    }
    if (xos.tenant().blessed_flavors.length == 0) {
        errors.push("no blessed flavors");
    }
    if (xos.tenant().blessed_images.length == 0) {
        errors.push("no blessed images");
    }
    if (xos.tenant().blessed_sites.length == 0) {
        errors.push("no blessed sites");
    }
    if (xos.tenant().current_user_site_id == null) {
        errors.push("current user does not have a site");
    }

    if (errors.length > 0) {
         t = templateFromId("#tenant-sanity-check")
         $("#tenantSummary").html( t({errors: errors, blessed_deployment_names: xos.tenant().blessed_deployment_names}) );
         return false;
    }

    return true;
}

XOSTenantApp.collectionLoadChange = function() {
    stats = xos.getCollectionStatus();

    if (!XOSTenantApp.navigationStarted) {
        if (stats["isLoaded"] + stats["failedLoad"] >= stats["startedLoad"]) {
            if (XOSTenantApp.sanityCheck()) {
                XOSTenantApp.viewSlice(undefined);
            }
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
/* eslint-enable */
