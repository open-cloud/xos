/* eslint-disable */
HTMLView = Marionette.ItemView.extend({
  render: function() {
      this.$el.append(this.options.html);
  },
});

FilteredCompositeView = Marionette.CompositeView.extend( {
    showCollection: function() {
      var ChildView;
      this.collection.each(function(child, index) {
        filterFunc = this.options.filter || this.filter;
        if (filterFunc && !filterFunc(child)) {
            return;
        }
        ChildView = this.getChildView(child);
        this.addChild(child, ChildView, index);
      }, this);

    },
});

SliceSelectorOption = Marionette.ItemView.extend({
    template: "#xos-sliceselector-option",
    tagName: "option",
    attributes: function() {
        if (this.options.selectedID == this.model.get("id")) {
            return { value: this.model.get("id"), selected: 1 };
        } else {
            return { value: this.model.get("id") };
        }
    },
});

SliceSelectorView = FilteredCompositeView.extend({
    template: "#xos-sliceselector-select",
    childViewContainer: "select",
    childView: SliceSelectorOption,
    caption: "Slice",

    events: {"change select": "onSliceChanged"},

    childViewOptions: function() {
        return { selectedID: this.options.selectedID || this.selectedID || null };
    },

    onSliceChanged: function() {
        this.sliceChanged(this.$el.find("select").val());
    },

    sliceChanged: function(id) {
        console.log("sliceChanged " + id);
    },

    templateHelpers: function() { return {caption: this.options.caption || this.caption }; },
});

XOSRouter = Marionette.AppRouter.extend({
        initialize: function() {
            this.routeStack=[];
        },

        onRoute: function(x,y,z) {
             this.routeStack.push(Backbone.history.fragment);
             this.routeStack = this.routeStack.slice(-32);   // limit the size of routeStack to something reasonable
        },

        prevPage: function() {
             return this.routeStack.slice(-1)[0];
        },

        showPreviousURL: function() {
            prevPage = this.prevPage();
            //console.log("showPreviousURL");
            //console.log(this.routeStack);
            if (prevPage) {
                this.navigate("#"+prevPage, {trigger: false, replace: true} );
            }
        },

        navigate: function(href, options) {
            if (options.force) {
                Marionette.AppRouter.prototype.navigate.call(this, "nowhere", {trigger: false, replace: true});
            }
            Marionette.AppRouter.prototype.navigate.call(this, href, options);
        },
    });

// XXX - We import backbone multiple times (BAD!) since the import happens
//   inside of the view's html. The second time it's imported (developer
//   view), it wipes out Backbone.Syphon. So, save it as Backbone_Syphon for
//   now.
Backbone_Syphon = Backbone.Syphon
Backbone_Syphon.InputReaders.register('select', function(el) {
    // Modify syphon so that if a select has "syphonall" in the class, then
    // the value of every option will be returned, regardless of whether of
    // not it is selected.
    if (el.hasClass("syphonall")) {
        result = [];
        _.each(el.find("option"), function(option) {
            result.push($(option).val());
        });
        return result;
    }
    return el.val();
});

XOSApplication = Marionette.Application.extend({
    detailBoxId: "#detailBox",
    errorBoxId: "#errorBox",
    errorCloseButtonId: "#close-error-box",
    successBoxId: "#successBox",
    successCloseButtonId: "#close-success-box",
    errorTemplate: "#xos-error-template",
    successTemplate: "#xos-success-template",
    logMessageCount: 0,

    confirmDialog: function(view, event, callback) {
        $("#xos-confirm-dialog").dialog({
           autoOpen: false,
           modal: true,
           buttons : {
                "Confirm" : function() {
                  $(this).dialog("close");
                  if (event) {
                      view.trigger(event);
                  }
                  if (callback) {
                      callback();
                  }
                },
                "Cancel" : function() {
                  $(this).dialog("close");
                }
              }
            });
        $("#xos-confirm-dialog").dialog("open");
    },

    popupErrorDialog: function(responseText) {
        try {
            parsed_error=$.parseJSON(responseText);
            width=300;
        }
        catch(err) {
            parsed_error=undefined;
            width=640;    // django stacktraces like wide width
        }

        console.log(responseText);
        console.log(parsed_error);

        if (parsed_error && ("detail" in parsed_error)) {
            parsed_error = parsed_error["detail"];
        }

        if (parsed_error && ("error" in parsed_error)) {
            if ((!parsed_error.reasons) && (parsed_error.fields)) {
                // deal with me renaming 'reasons' to 'fields'
                parsed_error.reasons = parsed_error.fields;
            }
            // this error comes from genapi views
            $("#xos-error-dialog").html(templateFromId("#xos-error-response")(parsed_error));
        } else {
            $("#xos-error-dialog").html(templateFromId("#xos-error-rawresponse")({responseText: strip_scripts(responseText)}))
        }

        $("#xos-error-dialog").dialog({
            modal: true,
            width: width,
            buttons: {
                Ok: function() { $(this).dialog("close"); }
            }
        });
    },

    hideLinkedItems: function(result) {
        var index=0;
        while (index<4) {
            this["linkedObjs" + (index+1)].empty();
            index = index + 1;
        }
    },

    hideTabs: function() { $("#tabs").hide(); },
    showTabs: function() { $("#tabs").show(); },

    createListHandler: function(listViewName, collection_name, regionName, title) {
        var app=this;
        return function() {
            listView = new app[listViewName];
            app[regionName].show(listView);
            app.hideLinkedItems();
            $("#contentTitle").html(templateFromId("#xos-title-list")({"title": title}));
            $(document).attr('title', title);
            $("#detail").show();
            app.hideTabs();

            listButtons = new XOSListButtonView({linkedView: listView});
            app["rightButtonPanel"].show(listButtons);
        }
    },

    createAddHandler: function(detailName, collection_name, regionName, title) {
        var app=this;
        return function() {
            console.log("addHandler");

            app.hideLinkedItems();
            app.hideTabs();

            model = new xos[collection_name].model();
            detailViewClass = app[detailName];
            detailView = new detailViewClass({model: model, collection:xos[collection_name]});
            app[regionName].show(detailView);

            detailButtons = new XOSDetailButtonView({linkedView: detailView});
            app["rightButtonPanel"].show(detailButtons);
        }
    },

    createAddChildHandler: function(addChildName, collection_name) {
        var app=this;
        return function(parent_modelName, parent_fieldName, parent_id) {
            app.Router.showPreviousURL();
            model = new xos[collection_name].model();
            model.attributes[parent_fieldName] = parent_id;
            model.readOnlyFields.push(parent_fieldName);
            detailViewClass = app[addChildName];
            var detailView = new detailViewClass({model: model, collection:xos[collection_name]});
            detailView.dialog = $("xos-addchild-dialog");
            app["addChildDetail"].show(detailView);
            $("#xos-addchild-dialog").dialog({
               autoOpen: false,
               modal: true,
               width: 640,
               buttons : {
                    "Save" : function() {
                      var addDialog = this;
                      detailView.synchronous = true;
                      detailView.afterSave = function() { console.log("addChild afterSave"); $(addDialog).dialog("close"); }
                      detailView.save();

                      //$(this).dialog("close");
                    },
                    "Cancel" : function() {
                      $(this).dialog("close");
                    }
                  }
                });
            $("#xos-addchild-dialog").dialog("open");
        }
    },

    createDeleteHandler: function(collection_name) {
        var app=this;
        return function(model_id) {
            console.log("deleteCalled");
            collection = xos[collection_name];
            model = collection.get(model_id);
            assert(model!=undefined, "failed to get model " + model_id + " from collection " + collection_name);
            app.Router.showPreviousURL();
            app.deleteDialog(model);
        }
    },

    createDetailHandler: function(detailName, collection_name, regionName, title) {
        var app=this;
        var detail_title=title;
        showModelId = function(model_id) {
            collection = xos[collection_name];
            model = collection.get(model_id);
            if (model == undefined) {
                app[regionName].show(new HTMLView({html: "failed to load object " + model_id + " from collection " + collection_name}));
            } else {
                var title = detail_title + ": " + model.attributes.humanReadableName;

                $("#contentTitle").html(templateFromId("#xos-title-detail")({"title": title}));

                $(document).attr('title', title);

                detailViewClass = app[detailName];
                detailView = new detailViewClass({model: model});
                app[regionName].show(detailView);
                detailView.showLinkedItems();

                detailButtons = new XOSDetailButtonView({linkedView: detailView});
                app["rightButtonPanel"].show(detailButtons);
            }
        }
        return showModelId;
    },

    /* error handling callbacks */

    hideError: function() {
        if (this.logWindowId) {
        } else {
            $(this.errorBoxId).hide();
            $(this.successBoxId).hide();
        }
    },

    showSuccess: function(result) {
         result["statusclass"] = "success";
         if (this.logTableId) {
             this.appendLogWindow(result);
         } else {
             $(this.successBoxId).show();
             $(this.successBoxId).html(_.template($(this.successTemplate).html())(result));
             var that=this;
             $(this.successCloseButtonId).unbind().bind('click', function() {
                 $(that.successBoxId).hide();
             });
         }
    },

    showError: function(result) {
         result["statusclass"] = "failure";
         if (this.logTableId) {
             this.appendLogWindow(result);
             this.popupErrorDialog(result.responseText);
         } else {
             // this is really old stuff
             $(this.errorBoxId).show();
             $(this.errorBoxId).html(_.template($(this.errorTemplate).html())(result));
             var that=this;
             $(this.errorCloseButtonId).unbind().bind('click', function() {
                 $(that.errorBoxId).hide();
             });
         }
    },

    showInformational: function(result) {
         result["statusclass"] = "inprog";
         if (this.logTableId) {
             return this.appendLogWindow(result);
         } else {
             return undefined;
         }
    },

    appendLogWindow: function(result) {
        // compute a new logMessageId for this log message
        logMessageId = "logMessage" + this.logMessageCount;
        this.logMessageCount = this.logMessageCount + 1;
        result["logMessageId"] = logMessageId;

        logMessageTemplate=$("#xos-log-template").html();
        assert(logMessageTemplate != undefined, "logMessageTemplate is undefined");
        newRow = _.template(logMessageTemplate, result);
        assert(newRow != undefined, "newRow is undefined");

        if (result["infoMsgId"] != undefined) {
            // We were passed the logMessageId of an informational message,
            // and the caller wants us to replace that message with our own.
            // i.e. replace an informational message with a success or an error.
            $("#"+result["infoMsgId"]).replaceWith(newRow);
        } else {
            // Create a brand new log message rather than replacing one.
            logTableBody = $(this.logTableId + " tbody");
            logTableBody.prepend(newRow);
        }

        if (this.statusMsgId) {
            $(this.statusMsgId).html( templateFromId("#xos-status-template")(result) );
        }

        limitTableRows(this.logTableId, 5);

        return logMessageId;
    },

    saveError: function(model, result, xhr, infoMsgId) {
        console.log("saveError");
        result["what"] = "save " + model.modelName + " " + model.attributes.humanReadableName;
        result["infoMsgId"] = infoMsgId;
        this.showError(result);
    },

    saveSuccess: function(model, result, xhr, infoMsgId, addToCollection) {
        console.log("saveSuccess");
        if (model.addToCollection) {
            console.log("addToCollection");
            console.log(model.addToCollection);
            model.addToCollection.add(model);
            model.addToCollection.sort();
            model.addToCollection = undefined;
        }
        result = {status: xhr.xhr.status, statusText: xhr.xhr.statusText};
        result["what"] = "save " + model.modelName + " " + model.attributes.humanReadableName;
        result["infoMsgId"] = infoMsgId;
        this.showSuccess(result);
    },

    destroyError: function(model, result, xhr, infoMsgId) {
        result["what"] = "destroy " + model.modelName + " " + model.attributes.humanReadableName;
        result["infoMsgId"] = infoMsgId;
        this.showError(result);
    },

    destroySuccess: function(model, result, xhr, infoMsgId) {
        result = {status: xhr.xhr.status, statusText: xhr.xhr.statusText};
        result["what"] = "destroy " + model.modelName + " " + model.attributes.humanReadableName;
        result["infoMsgId"] = infoMsgId;
        this.showSuccess(result);
    },

    /* end error handling callbacks */

    destroyModel: function(model) {
         //console.log("destroyModel"); console.log(model);
         this.hideError();
         var infoMsgId = this.showInformational( {what: "destroy " + model.modelName + " " + model.attributes.humanReadableName, status: "", statusText: "in progress..."} );
         var that = this;
         model.destroy({error: function(model, result, xhr) { that.destroyError(model,result,xhr,infoMsgId);},
                        success: function(model, result, xhr) { that.destroySuccess(model,result,xhr,infoMsgId);}});
    },

    deleteDialog: function(model, afterDelete) {
        var that=this;
        assert(model!=undefined, "deleteDialog's model is undefined");
        //console.log("deleteDialog"); console.log(model);
        this.confirmDialog(null, null, function() {
            //console.log("deleteConfirm"); console.log(model);
            modelName = model.modelName;
            that.destroyModel(model);
            if (afterDelete=="list") {
                that.navigate("list", modelName);
            } else if (afterDelete) {
                afterDelete();
            }
        });
    },
});

XOSButtonView = Marionette.ItemView.extend({
            events: {"click button.btn-xos-save-continue": "submitContinueClicked",
                     "click button.btn-xos-save-leave": "submitLeaveClicked",
                     "click button.btn-xos-save-another": "submitAddAnotherClicked",
                     "click button.btn-xos-delete": "deleteClicked",
                     "click button.btn-xos-add": "addClicked",
                     "click button.btn-xos-refresh": "refreshClicked",
                     },

            submitLeaveClicked: function(e) {
                     this.options.linkedView.submitLeaveClicked.call(this.options.linkedView, e);
                     },

            submitContinueClicked: function(e) {
                     this.options.linkedView.submitContinueClicked.call(this.options.linkedView, e);
                     },

            submitAddAnotherClicked: function(e) {
                     this.options.linkedView.submitAddAnotherClicked.call(this.options.linkedView, e);
                     },

            submitDeleteClicked: function(e) {
                     this.options.linkedView.deleteClicked.call(this.options.linkedView, e);
                     },

            addClicked: function(e) {
                     this.options.linkedView.addClicked.call(this.options.linkedView, e);
                     },

            refreshClicked: function(e) {
                     this.options.linkedView.refreshClicked.call(this.options.linkedView, e);
                     },

            templateHelpers: function() { return {disableAdd: this.options.linkedView.disableAdd }; },
            });


XOSDetailButtonView = XOSButtonView.extend({ template: "#xos-savebuttons-template" });
XOSListButtonView = XOSButtonView.extend({ template: "#xos-listbuttons-template" });

/* XOSDetailView
      extend with:
         app - MarionetteApplication
         template - template (See XOSHelper.html)
*/

XOSDetailView = Marionette.ItemView.extend({
            tagName: "div",

            viewInitializers: [],

            events: {"click button.btn-xos-save-continue": "submitContinueClicked",
                     "click button.btn-xos-save-leave": "submitLeaveClicked",
                     "click button.btn-xos-save-another": "submitAddAnotherClicked",
                     "click button.btn-xos-delete": "deleteClicked",
                     "change input": "inputChanged"},

            /* inputChanged is watching the onChange events of the input controls. We
               do this to track when this view is 'dirty', so we can throw up a warning
               if the user tries to change his slices without saving first.
            */

            initialize: function() {
                this.on("saveSuccess", this.onSaveSuccess);
                this.synchronous = false;
            },

            onShow: function() {
                _.each(this.viewInitializers, function(initializer) {
                    initializer();
                });
            },

            saveSuccess: function(e) {
                // always called after a save succeeds
            },

            afterSave: function(e) {
                // if this.synchronous, then called after the save succeeds
                // if !this.synchronous, then called after save is initiated
            },

            onSaveSuccess: function(e) {
                this.saveSuccess(e);
                if (this.synchronous) {
                    this.afterSave(e);
                }
            },

            inputChanged: function(e) {
                this.dirty = true;
            },

            submitContinueClicked: function(e) {
                console.log("saveContinue");
                e.preventDefault();
                this.afterSave = function() { };
                this.save();
            },

            submitLeaveClicked: function(e) {
                console.log("saveLeave");
                e.preventDefault();
                if (this.options.noSubmitButton || this.noSubmitButton) {
                    return;
                }
                var that=this;
                this.afterSave = function() {
                    that.app.navigate("list", that.model.modelName);
                }
                this.save();
            },

            submitAddAnotherClicked: function(e) {
                console.log("saveAnother");
                console.log(this);
                e.preventDefault();
                var that=this;
                this.afterSave = function() {
                    console.log("addAnother afterSave");
                    that.app.navigate("add", that.model.modelName);
                }
                this.save();
            },

            save: function() {
                this.app.hideError();
                var data = Backbone_Syphon.serialize(this);
                var that = this;
                var isNew = !this.model.id;

                console.log('data', data);

                this.$el.find(".help-inline").remove();

                /* although model.validate() is called automatically by
                   model.save, we call it ourselves, so we can throw up our
                   validation error before creating the infoMsg in the log
                */
               
                errors =  this.model.xosValidate(data);

                if (errors) {
                    this.onFormDataInvalid(errors);
                    return;
                }

                if (isNew) {
                    this.model.attributes.humanReadableName = "new " + this.model.modelName;
                    this.model.addToCollection = this.collection;
                } else {
                    this.model.addToCollection = undefined;
                }

                var infoMsgId = this.app.showInformational( {what: "save " + this.model.modelName + " " + this.model.attributes.humanReadableName, status: "", statusText: "in progress..."} );

                this.model.save(data, {error: function(model, result, xhr) { that.app.saveError(model,result,xhr,infoMsgId);},
                                       success: function(model, result, xhr) { that.app.saveSuccess(model,result,xhr,infoMsgId);
                                                                               that.trigger("saveSuccess");
                                                                             }});
                this.dirty = false;

                if (!this.synchronous) {
                    this.afterSave();
                }
            },

            deleteClicked: function(e) {
                e.preventDefault();
                this.app.deleteDialog(this.model, "list");
            },

            tabClick: function(tabId, regionName) {
                    region = this.app[regionName];
                    if (this.currentTabRegion != undefined) {
                        this.currentTabRegion.$el.hide();
                    }
                    if (this.currentTabId != undefined) {
                        $(this.currentTabId).removeClass('active');
                    }
                    this.currentTabRegion = region;
                    this.currentTabRegion.$el.show();

                    this.currentTabId = tabId;
                    $(tabId).addClass('active');
            },

            showTabs: function(tabs) {
                template = templateFromId("#xos-tabs-template", {tabs: tabs});
                $("#tabs").html(template(tabs));
                var that = this;

                _.each(tabs, function(tab) {
                    var regionName = tab["region"];
                    var tabId = '#xos-nav-'+regionName;
                    $(tabId).bind('click', function() { that.tabClick(tabId, regionName); });
                });

                $("#tabs").show();
            },

            showLinkedItems: function() {
                    tabs=[];

                    tabs.push({name: "details", region: "detail"});

                    makeFilter = function(relatedField, relatedId) {
                        return function(model) { return model.attributes[relatedField] == relatedId; }
                    };

                    var index=0;
                    for (relatedName in this.model.collection.relatedCollections) {
                        var relatedField = this.model.collection.relatedCollections[relatedName];
                        var relatedId = this.model.id;
                        regionName = "linkedObjs" + (index+1);

                        relatedListViewClassName = relatedName + "ListView";
                        assert(this.app[relatedListViewClassName] != undefined, relatedListViewClassName + " not found");
                        relatedListViewClass = this.app[relatedListViewClassName].extend({collection: xos[relatedName],
                                                                                          filter: makeFilter(relatedField, relatedId),
                                                                                          parentModel: this.model});
                        this.app[regionName].show(new relatedListViewClass());
                        if (this.app.hideTabsByDefault) {
                            this.app[regionName].$el.hide();
                        }
                        tabs.push({name: relatedName, region: regionName});
                        index = index + 1;
                    }

                    while (index<4) {
                        this.app["linkedObjs" + (index+1)].empty();
                        index = index + 1;
                    }

                    this.showTabs(tabs);
                    this.tabClick('#xos-nav-detail', 'detail');
              },

            onFormDataInvalid: function(errors) {


                var self=this;

                var markErrors = function(value, key) {
                    var $inputElement = self.$el.find("[name='" + key + "']");
                    var $inputContainer = $inputElement.parent();
                    //$inputContainer.find(".help-inline").remove();
                    // var $errorEl = $("<span>", {class: "help-inline error", text: value});
                    $inputContainer.find(".alert.alert-danger").remove();
                    var $errorEl = $("<span>", {class: "alert alert-danger", text: value});
                    $inputContainer.append($errorEl).addClass("error");
                }
                _.each(errors, markErrors);
            },

             templateHelpers: function() { return { modelName: this.model.modelName,
                                                    collectionName: this.model.collectionName,
                                                    addFields: this.model.addFields,
                                                    listFields: this.model.listFields,
                                                    detailFields: this.options.detailFields || this.detailFields || this.model.detailFields,
                                                    fieldDisplayNames: this.options.fieldDisplayNames || this.fieldDisplayNames || this.model.fieldDisplayNames || {},
                                                    foreignFields: this.model.foreignFields,
                                                    detailLinkFields: this.model.detailLinkFields,
                                                    inputType: this.model.inputType,
                                                    model: this.model,
                                                    detailView: this,
                                                    choices: this.options.choices || this.choices || this.model.choices || {},
                                                    helpText: this.options.helpText || this.helpText || this.model.helpText || {},
                                         }},

             disableAdd: function() { return this.disableAdd || this.options.disableAdd || this.model.disableAdd; },
});

XOSDetailView_instance = XOSDetailView.extend( {
    events: $.extend(XOSDetailView.events,
        {"change #field_deployment": "onDeploymentChange"}
    ),

    onShow: function() {
        // Note that this causes the selects to be updated a second time. The
        // first time was when the template was originally invoked, and the
        // selects will all have the full unfiltered set of candidates. Then
        // onShow will fire, and we'll update them with the filtered values.
        this.onDeploymentChange();
    },

    onDeploymentChange: function(e) {
        var deploymentID = this.$el.find("#field_deployment").val();

        //console.log("onDeploymentChange");

        filterFunc = function(model) { for (index in xos.siteDeployments.models) {
                                           site_deployment = xos.siteDeployments.models[index];
                                           if (site_deployment.attributes.id == model.attributes.site_deployment) {
                                               return (site_deployment.attributes.deployment == deploymentID);
                                           }
                                        }
                                        return false;
                                        // return (model.attributes.deployment==deploymentID); }
                                      };
        newSelect = idToSelect("node",
                               this.model.attributes.node,
                               this.model.foreignFields["node"],
                               "humanReadableName",
                               false,
                               filterFunc);
        this.$el.find("#field_node").html(newSelect);

        filterFunc = function(model) { for (index in model.attributes.deployments) {
                                          if (model.attributes.deployments[index] == deploymentID) return true;
                                        };
                                        return false;
                                     }
        newSelect = idToSelect("flavor",
                               this.model.attributes.flavor,
                               this.model.foreignFields["flavor"],
                               "humanReadableName",
                               false,
                               filterFunc);
        this.$el.find("#field_flavor").html(newSelect);

        filterFunc = function(model) { for (index in model.attributes.deployments) {
                                           if (model.attributes.deployments[index] == deploymentID) return true;
                                       };
                                       return false;
                                     };
        newSelect = idToSelect("image",
                               this.model.attributes.image,
                               this.model.foreignFields["image"],
                               "humanReadableName",
                               false,
                               filterFunc);
        this.$el.find("#field_image").html(newSelect);
    },
});

/* XOSItemView
      This is for items that will be displayed as table rows.
      extend with:
         app - MarionetteApplication
         template - template (See XOSHelper.html)
*/

XOSItemView = Marionette.ItemView.extend({
             tagName: 'tr',
             className: 'test-tablerow',

             templateHelpers: function() { return { modelName: this.model.modelName,
                                                    collectionName: this.model.collectionName,
                                                    listFields: this.model.listFields,
                                                    addFields: this.model.addFields,
                                                    detailFields: this.model.detailFields,
                                                    foreignFields: this.model.foreignFields,
                                                    detailLinkFields: this.model.detailLinkFields,
                                                    inputType: this.model.inputType,
                                                    model: this.model,
                                         }},
});

/* XOSListView:
      extend with:
         app - MarionetteApplication
         childView - class of ItemView, probably an XOSItemView
         template - template (see xosHelper.html)
         collection - collection that holds these objects
         title - title to display in template
*/

XOSListView = FilteredCompositeView.extend({
             childViewContainer: 'tbody',
             parentModel: null,

             events: {"click button.btn-xos-add": "addClicked",
                      "click button.btn-xos-refresh": "refreshClicked",
                     },

             _fetchStateChange: function() {
                 if (this.collection.fetching) {
                    $("#xos-list-title-spinner").show();
                 } else {
                    $("#xos-list-title-spinner").hide();
                 }
             },

             addClicked: function(e) {
                e.preventDefault();
                this.app.Router.navigate("add" + firstCharUpper(this.collection.modelName), {trigger: true});
             },

             refreshClicked: function(e) {
                 e.preventDefault();
                 this.collection.refresh(refreshRelated=true);
             },

             initialize: function() {
                 this.listenTo(this.collection, 'change', this._renderChildren)
                 this.listenTo(this.collection, 'sort', function() { console.log("sort"); })
                 this.listenTo(this.collection, 'add', function() { console.log("add"); })
                 this.listenTo(this.collection, 'fetchStateChange', this._fetchStateChange);

                 // Because many of the templates use idToName(), we need to
                 // listen to the collections that hold the names for the ids
                 // that we want to display.
                 for (i in this.collection.foreignCollections) {
                     foreignName = this.collection.foreignCollections[i];
                     if (xos[foreignName] == undefined) {
                         console.log("Failed to find xos class " + foreignName);
                     }
                     this.listenTo(xos[foreignName], 'change', this._renderChildren);
                     this.listenTo(xos[foreignName], 'sort', this._renderChildren);
                 }
             },

             getAddChildHash: function() {
                if (this.parentModel) {
                    parentFieldName = this.parentModel.relatedCollections[this.collection.collectionName];
                    parentFieldName = parentFieldName || "unknown";

                    /*parentFieldName = "unknown";

                    for (fieldName in this.collection.foreignFields) {
                        cname = this.collection.foreignFields[fieldName];
                        if (cname = this.collection.collectionName) {
                            parentFieldName = fieldName;
                        }
                    }*/
                    return "#addChild" + firstCharUpper(this.collection.modelName) + "/" + this.parentModel.modelName + "/" + parentFieldName + "/" + this.parentModel.id; // modelName, fieldName, id
                } else {
                    return null;
                }
             },

             templateHelpers: function() {
                return { title: this.title,
                         addChildHash: this.getAddChildHash(),
                         foreignFields: this.collection.foreignFields,
                         listFields: this.collection.listFields,
                         detailLinkFields: this.collection.detailLinkFields, };
             },

             disableAdd: function() { return this.disableAdd || this.options.disableAdd || this.collection.disableAdd; }
});

XOSDataTableView = Marionette.View.extend( {
    el: '<div style="overflow: hidden">' +
        '<h3 class="xos-list-title title_placeholder"></h3>' +
        '<div class="header_placeholder"></div>' +
        '<table></table>' +
        '<div class="footer_placeholder"></div>' +
        '</div>',

    filter: undefined,

     events: {"click button.btn-xos-add": "addClicked",
              "click button.btn-xos-refresh": "refreshClicked",
             },

     _fetchStateChange: function() {
         if (this.collection.fetching) {
            $("#xos-list-title-spinner").show();
         } else {
            $("#xos-list-title-spinner").hide();
         }
     },

     addClicked: function(e) {
        e.preventDefault();
        this.app.Router.navigate("add" + firstCharUpper(this.collection.modelName), {trigger: true});
     },

     refreshClicked: function(e) {
         e.preventDefault();
         this.collection.refresh(refreshRelated=true);
     },


    initialize: function() {
        $(this.el).find(".footer_placeholder").html( xosListFooterTemplate({addChildHash: this.getAddChildHash()}) );
        $(this.el).find(".header_placeholder").html( xosListHeaderTemplate() );

        this.listenTo(this.collection, 'fetchStateChange', this._fetchStateChange);
    },

    render: function() {
        var view = this;
        var fieldDisplayNames = view.options.fieldDisplayNames || view.fieldDisplayNames || {};

        view.columnsByIndex = [];
        view.columnsByFieldName = {};
        _.each(this.collection.listFields, function(fieldName) {
            inputType = view.options.inputType || view.inputType || {};
            mRender = undefined;
            mSearchText = undefined;
            sTitle = fieldName in fieldDisplayNames ? fieldDisplayNames[fieldName] : fieldNameToHumanReadable(fieldName);
            bSortable = true;
            if (fieldName=="backend_status") {
                mRender = function(x,y,z) { return xosBackendStatusIconTemplate(z); };
                sTitle = "";
                bSortable = false;
            } else if (fieldName in view.collection.foreignFields) {
                var foreignCollection = view.collection.foreignFields[fieldName];
                mSearchText = function(x) { return idToName(x, foreignCollection, "humanReadableName"); };
            } else if (inputType[fieldName] == "spinner") {
                mRender = function(x,y,z) { return xosDataTableSpinnerTemplate( {value: x, collectionName: view.collection.collectionName, fieldName: fieldName, id: z.id, app: view.app} ); };
            }
            if ($.inArray(fieldName, view.collection.detailLinkFields)>=0) {
                var collectionName = view.collection.collectionName;
                mRender = function(x,y,z) { return '<a href="#' + collectionName + '/' + z.id + '">' + x + '</a>'; };
            }
            thisColumn = {sTitle: sTitle, bSortable: bSortable, mData: fieldName, mRender: mRender, mSearchText: mSearchText};
            view.columnsByIndex.push( thisColumn );
            view.columnsByFieldName[fieldName] = thisColumn;
        });

        if (!view.noDeleteColumn) {
            deleteColumn = {sTitle: "", bSortable: false, mRender: function(x,y,z) { return xosDeleteButtonTemplate({modelName: view.collection.modelName, id: z.id}); }, mData: function() { return "delete"; }};
            view.columnsByIndex.push(deleteColumn);
            view.columnsByFieldName["delete"] = deleteColumn;
        };

        oTable = $(this.el).find("table").dataTable( {
            "bJQueryUI": true,
            "bStateSave": true,
            "bServerSide": true,
            "bFilter": ! (view.options.disableFilter || view.disableFilter),
            "bPaginate": ! (view.options.disablePaginate || view.disablePaginate),
            "aoColumns": view.columnsByIndex,

            fnServerData: function(sSource, aoData, fnCallback, settings) {
                var compareColumns = function(sortCols, sortDirs, a, b) {
                    a = a[sortCols[0]];
                    b = b[sortCols[0]];
                    result = (a==b) ? 0 : ((a<b) ? -1 : 1);
                    if (sortDirs[0] == "desc") {
                        result = -result;
                    }
                    return result;
                };

                var searchMatch = function(row, sSearch) {
                    for (fieldName in row) {
                        if (fieldName in view.columnsByFieldName) {
                            try {
                                value = row[fieldName].toString();
                            } catch(e) {
                                continue;
                            }
                            if (value.indexOf(sSearch) >= 0) {
                                return true;
                            }
                        }
                    }
                    return false;
                };

                //console.log(aoData);

                // function used to populate the DataTable with the current
                // content of the collection
                var populateTable = function()
                {
                  //console.log("populatetable!");

                  // clear out old row views
                  rows = [];

                  sSearch = null;
                  iDisplayStart = 0;
                  iDisplayLength = 1000;
                  sortDirs = [];
                  sortCols = [];
                  _.each(aoData, function(param) {
                      if (param.name == "sSortDir_0") {
                          sortDirs = [param.value];
                      } else if (param.name == "iSortCol_0") {
                          sortCols = [view.columnsByIndex[param.value].mData];
                      } else if (param.name == "iDisplayStart") {
                          iDisplayStart = param.value;
                      } else if (param.name == "iDisplayLength") {
                          iDisplayLength = param.value;
                      } else if (param.name == "sSearch") {
                          sSearch = param.value;
                      }
                  });

                  aaData = view.collection.toJSON();

                  // apply backbone filtering on the models
                  if (view.filter) {
                      aaData = aaData.filter( function(row) { model = {}; model.attributes = row; return view.filter(model); } );
                  }

                  var totalSize = aaData.length;

                  // turn the ForeignKey fields into human readable things
                  for (rowIndex in aaData) {
                      row = aaData[rowIndex];
                      for (fieldName in row) {
                          if (fieldName in view.columnsByFieldName) {
                              mSearchText = view.columnsByFieldName[fieldName].mSearchText;
                              if (mSearchText) {
                                  row[fieldName] = mSearchText(row[fieldName]);
                              }
                          }
                      }
                  }

                  // apply datatables search
                  if (sSearch) {
                      aaData = aaData.filter( function(row) { return searchMatch(row, sSearch); });
                  }

                  var filteredSize = aaData.length;

                  // apply datatables sort
                  aaData.sort(function(a,b) { return compareColumns(sortCols, sortDirs, a, b); });

                  // slice it for pagination
                  if (iDisplayLength >= 0) {
                      aaData = aaData.slice(iDisplayStart, iDisplayStart+iDisplayLength);
                  }

                  return fnCallback({iTotalRecords: totalSize,
                         iTotalDisplayRecords: filteredSize,
                         aaData: aaData});
                };

                aoData.shift(); // ignore sEcho
                populateTable();

                view.listenTo(view.collection, 'change', populateTable);
                view.listenTo(view.collection, 'add', populateTable);
                view.listenTo(view.collection, 'remove', populateTable);
            },
        } );

        return this;
    },

     getAddChildHash: function() {
        if (this.parentModel) {
            parentFieldName = this.parentModel.relatedCollections[this.collection.collectionName];
            parentFieldName = parentFieldName || "unknown";

            /*parentFieldName = "unknown";

            for (fieldName in this.collection.foreignFields) {
                cname = this.collection.foreignFields[fieldName];
                if (cname = this.collection.collectionName) {
                    parentFieldName = fieldName;
                }
            }*/
            return "#addChild" + firstCharUpper(this.collection.modelName) + "/" + this.parentModel.modelName + "/" + parentFieldName + "/" + this.parentModel.id; // modelName, fieldName, id
        } else {
            return null;
        }
     },

     disableAdd: function() { return this.disableAdd || this.options.disableAdd || this.collection.disableAdd; },

});

idToName = function(id, collectionName, fieldName) {
    return xos.idToName(id, collectionName, fieldName);
};

makeIdToName = function(collectionName, fieldName) {
    return function(id) { return idToName(id, collectionName, fieldName); }
};

/* Constructs lists of <option> html blocks for items in a collection.

   selectedId = the id of an object that should be selected, if any
   collectionName = name of collection
   fieldName = name of field within models of collection that will be displayed
*/

idToOptions = function(selectedId, collectionName, fieldName, filterFunc) {
    result=""
    for (index in xos[collectionName].models) {
        linkedObject = xos[collectionName].models[index];
        linkedId = linkedObject["id"];
        linkedName = linkedObject.attributes[fieldName];
        if (linkedId == selectedId) {
            selected = " selected";
        } else {
            selected = "";
        }
        if ((filterFunc) && (!filterFunc(linkedObject))) {
            continue;
        }
        result = result + '<option value="' + linkedId + '"' + selected + '>' + linkedName + '</option>';
    }
    return result;
};

/* Constructs an html <select> and the <option>s to go with it.

   variable = variable name to return to form
   selectedId = the id of an object that should be selected, if any
   collectionName = name of collection
   fieldName = name of field within models of collection that will be displayed
*/

idToSelect = function(variable, selectedId, collectionName, fieldName, readOnly, filterFunc) {
    if (readOnly) {
        readOnly = " readonly";
    } else {
        readOnly = "";
    }
    result = '<select class="form-control" name="' + variable + '" id="field_' + variable + '"' + readOnly + '>' +
             idToOptions(selectedId, collectionName, fieldName, filterFunc) +
             '</select>';
    return result;
}

choicesToOptions = function(selectedValue, choices) {
    result="";
    for (index in choices) {
        choice = choices[index];
        displayName = choice[0];
        value = choice[1];
        if (value == selectedValue) {
            selected = " selected";
        } else {
            selected = "";
        }
        result = result + '<option value="' + value + '"' + selected + '>' + displayName + '</option>';
    }
    return result;
}

choicesToSelect = function(variable, selectedValue, choices) {
    result = '<select class="form-control" name="' + variable + '" id="field_' + variable + '">' +
             choicesToOptions(selectedValue, choices) +
             '</select>';
    return result;
}

escapeForFormField = function(s) {
    if (s===undefined) {
        return "";
    } else {
        return String(s).replace(/"/g,'&quot;')
    }
}
/* eslint-enable */