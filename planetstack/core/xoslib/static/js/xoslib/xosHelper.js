function assert(outcome, description) {
    if (!outcome) {
        console.log(description);
    }
}

function templateFromId(id) {
    return _.template($(id).html());
}

function firstCharUpper(s) {
    return s.charAt(0).toUpperCase() + s.slice(1);
}

HTMLView = Marionette.ItemView.extend({
  render: function() {
      this.$el.append(this.options.html);
  },
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
        if (parsed_error) {
            $("#xos-error-dialog").html(templateFromId("#xos-error-response")(parsed_error));
        } else {
            $("#xos-error-dialog").html(templateFromId("#xos-error-rawresponse")({responseText: responseText}))
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

    listViewShower: function(listViewName, collection_name, regionName, title) {
        var app=this;
        return function() {
            app[regionName].show(new app[listViewName]);
            app.hideLinkedItems();
            $("#contentTitle").html(templateFromId("#xos-title-list")({"title": title}));
            $("#detail").show();
            $("#xos-listview-button-box").show();
            $("#tabs").hide();
            $("#xos-detail-button-box").hide();
        }
    },

    addShower: function(detailName, collection_name, regionName, title) {
        var app=this;
        return function() {
            model = new xos[collection_name].model();
            detailViewClass = app[detailName];
            detailView = new detailViewClass({model: model, collection:xos[collection_name]});
            app[regionName].show(detailView);
            $("#xos-detail-button-box").show();
            $("#xos-listview-button-box").hide();
        }
    },

    detailShower: function(detailName, collection_name, regionName, title) {
        var app=this;
        showModelId = function(model_id) {
            $("#contentTitle").html(templateFromId("#xos-title-detail")({"title": title}));

            collection = xos[collection_name];
            model = collection.get(model_id);
            if (model == undefined) {
                app[regionName].show(new HTMLView({html: "failed to load object " + model_id + " from collection " + collection_name}));
            } else {
                detailViewClass = app[detailName];
                detailView = new detailViewClass({model: model});
                app[regionName].show(detailView);
                detailView.showLinkedItems();
                $("#xos-detail-button-box").show();
                $("#xos-listview-button-box").hide();
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
        if (addToCollection) {
            addToCollection.add(model);
            addToCollection.sort();
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
         this.hideError();
         var infoMsgId = this.showInformational( {what: "destroy " + model.modelName + " " + model.attributes.humanReadableName, status: "", statusText: "in progress..."} );
         var that = this;
         model.destroy({error: function(model, result, xhr) { that.destroyError(model,result,xhr,infoMsgId);},
                        success: function(model, result, xhr) { that.destroySuccess(model,result,xhr,infoMsgId);}});
    },

    deleteDialog: function(model, navToListAfterDelete) {
        var that=this;
        this.confirmDialog(this, callback=function() {
            modelName = model.modelName;
            that.destroyModel(model);
            if (navToListAfterDelete) {
                that.navigate("list", modelName);
            }

        });
    },
});

/* XOSDetailView
      extend with:
         app - MarionetteApplication
         template - template (See XOSHelper.html)
*/

XOSDetailView = Marionette.ItemView.extend({
            tagName: "div",

            events: {"click button.btn-xos-save-continue": "submitContinueClicked",
                     "click button.btn-xos-save-leave": "submitLeaveClicked",
                     "click button.btn-xos-save-another": "submitAddAnotherClicked",
                     "click button.btn-xos-delete": "deleteClicked",
                     "change input": "inputChanged"},

            initialize: function() {
                this.on('deleteConfirmed', this.deleteConfirmed);
            },

            /* inputChanged is watching the onChange events of the input controls. We
               do this to track when this view is 'dirty', so we can throw up a warning
               if the user tries to change his slices without saving first.
            */

            inputChanged: function(e) {
                this.dirty = true;
            },

            submitContinueClicked: function(e) {
                console.log("saveContinue");
                e.preventDefault();
                this.save();
            },

            submitLeaveClicked: function(e) {
                console.log("saveLeave");
                e.preventDefault();
                this.save();
                this.app.navigate("list", this.model.modelName);
            },

            submitAddAnotherClicked: function(e) {
                console.log("saveAnother");
                e.preventDefault();
                this.save();
                this.app.navigate("add", this.model.modelName);
            },

            save: function() {
                this.app.hideError();
                var data = Backbone.Syphon.serialize(this);
                var that = this;
                var isNew = !this.model.id;

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
                    this.model.attributes.humanReadableName = "new " + model.modelName;
                    this.model.addToCollection = this.collection;
                } else {
                    this.model.addToCollection = undefined;
                }

                var infoMsgId = this.app.showInformational( {what: "save " + model.modelName + " " + model.attributes.humanReadableName, status: "", statusText: "in progress..."} );

                this.model.save(data, {error: function(model, result, xhr) { that.app.saveError(model,result,xhr,infoMsgId);},
                                       success: function(model, result, xhr) { that.app.saveSuccess(model,result,xhr,infoMsgId);}});
                this.dirty = false;
            },

            destroyModel: function() {
                 this.app.hideError();
                 var infoMsgId = this.app.showInformational( {what: "destroy " + model.modelName + " " + model.attributes.humanReadableName, status: "", statusText: "in progress..."} );
                 var that = this;
                 this.model.destroy({error: function(model, result, xhr) { that.app.destroyError(model,result,xhr,infoMsgId);},
                                     success: function(model, result, xhr) { that.app.destroySuccess(model,result,xhr,infoMsgId);}});
            },

             deleteClicked: function(e) {
                 e.preventDefault();
                 this.app.confirmDialog(this, "deleteConfirmed");
             },

             deleteConfirmed: function() {
                 modelName = this.model.modelName;
                 this.destroyModel();
                 this.app.navigate("list", modelName);
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

                    var index=0;
                    for (relatedName in this.model.collection.relatedCollections) {
                        relatedField = this.model.collection.relatedCollections[relatedName];
                        regionName = "linkedObjs" + (index+1);

                        relatedListViewClassName = relatedName + "ListView";
                        assert(this.app[relatedListViewClassName] != undefined, relatedListViewClassName + " not found");
                        relatedListViewClass = this.app[relatedListViewClassName].extend({collection: xos[relatedName].filterBy(relatedField,this.model.id)});
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
                    console.log("name='" + key + "'");
                    var $inputElement = self.$el.find("[name='" + key + "']");
                    var $inputContainer = $inputElement.parent();
                    //$inputContainer.find(".help-inline").remove();
                    var $errorEl = $("<span>", {class: "help-inline error", text: value});
                    $inputContainer.append($errorEl).addClass("error");
                }
                _.each(errors, markErrors);
            },

});

/* XOSItemView
      This is for items that will be displayed as table rows.
      extend with:
         app - MarionetteApplication
         template - template (See XOSHelper.html)
         detailClass - class of detail view, probably an XOSDetailView
*/

XOSItemView = Marionette.ItemView.extend({
             tagName: 'tr',
             className: 'test-tablerow',

             templateHelpers: function() { return { modelName: this.model.modelName,
                                                    collectionName: this.model.collectionName,
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

XOSListView = Marionette.CompositeView.extend({
             childViewContainer: 'tbody',

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

             templateHelpers: function() {
                return { title: this.title };
             },
});

/* Give an id, the name of a collection, and the name of a field for models
   within that collection, lookup the id and return the value of the field.
*/

idToName = function(id, collectionName, fieldName) {
    linkedObject = xos[collectionName].get(id);
    if (linkedObject == undefined) {
        return "#" + id;
    } else {
        return linkedObject.attributes[fieldName];
    }
};

/* Constructs lists of <option> html blocks for items in a collection.

   selectedId = the id of an object that should be selected, if any
   collectionName = name of collection
   fieldName = name of field within models of collection that will be displayed
*/

idToOptions = function(selectedId, collectionName, fieldName) {
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

idToSelect = function(variable, selectedId, collectionName, fieldName) {
    result = '<select name="' + variable + '">' +
             idToOptions(selectedId, collectionName, fieldName) +
             '</select>';
    return result;
}

