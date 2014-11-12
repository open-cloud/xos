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

    hideError: function() {
        if (this.logWindowId) {
        } else {
            $(this.errorBoxId).hide();
            $(this.successBoxId).hide();
        }
    },

    showSuccess: function(result) {
         result["success"] = "success";
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
         result["success"] = "failure";
         if (this.logTableId) {
             this.appendLogWindow(result);
         } else {
             $(this.errorBoxId).show();
             $(this.errorBoxId).html(_.template($(this.errorTemplate).html())(result));
             var that=this;
             $(this.errorCloseButtonId).unbind().bind('click', function() {
                 $(that.errorBoxId).hide();
             });
         }
    },

    showInformational: function(result) {
         result["success"] = "information";
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

        return logMessageId;
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
            detailView = new detailViewClass({model: model});
            app[regionName].show(detailView);
            $("#xos-detail-button-box").show();
            $("#xos-listview-button-box").hide();
        }
    },

    detailShower: function(detailName, collection_name, regionName, title) {
        var app=this;
        showModelId = function(model_id) {
            showModel = function(model) {
                detailViewClass = app[detailName];
                detailView = new detailViewClass({model: model});
                app[regionName].show(detailView);
                detailView.showLinkedItems();
                $("#xos-detail-button-box").show();
                $("#xos-listview-button-box").hide();
            }

            $("#contentTitle").html(templateFromId("#xos-title-detail")({"title": title}));

            collection = xos[collection_name];
            model = collection.get(model_id);
            if (model == undefined) {
                if (!collection.isLoaded) {
                    // If the model cannot be found, then maybe it's because
                    // we haven't finished loading the collection yet. So wait for
                    // the sort event to complete, then try again.
                    collection.once("sort", function() {
                        collection = xos[collection_name];
                        model = collection.get(model_id);
                        if (model == undefined) {
                            // We tried. It's not here. Complain to the user.
                            app[regionName].show(new HTMLView({html: "failed to load object " + model_id + " from collection " + collection_name}));
                        } else {
                            showModel(model);
                        }
                    });
                } else {
                    // The collection was loaded, the user must just be asking for something we don't have.
                    app[regionName].show(new HTMLView({html: "failed to load object " + model_id + " from collection " + collection_name}));
                }
            } else {
                showModel(model);
            }
        }
        return showModelId;
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
                     "change input": "inputChanged"},

            /* inputChanged is watching the onChange events of the input controls. We
               do this to track when this view is 'dirty', so we can throw up a warning
               if the user tries to change his slices without saving first.
            */

            inputChanged: function(e) {
                this.dirty = true;
            },

            saveError: function(model, result, xhr, infoMsgId) {
                result["what"] = "save " + model.__proto__.modelName;
                result["infoMsgId"] = infoMsgId;
                this.app.showError(result);
            },

            saveSuccess: function(model, result, xhr, infoMsgId) {
                result = {status: xhr.xhr.status, statusText: xhr.xhr.statusText};
                result["what"] = "save " + model.__proto__.modelName;
                result["infoMsgId"] = infoMsgId;
                this.app.showSuccess(result);
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
            },

            submitAddAnotherClicked: function(e) {
                console.log("saveAnother");
                e.preventDefault();
                this.save();
            },

            save: function() {
                this.app.hideError();
                var infoMsgId = this.app.showInformational( {what: "save " + this.model.__proto__.modelName, status: "", statusText: "in progress..."} );
                var data = Backbone.Syphon.serialize(this);
                var that = this;
                this.model.save(data, {error: function(model, result, xhr) { that.saveError(model,result,xhr,infoMsgId);},
                                       success: function(model, result, xhr) { that.saveSuccess(model,result,xhr,infoMsgId);}});
                this.dirty = false;
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

             events: {"click": "changeItem"},

             changeItem: function(e) {
                    this.app.hideError();
                    e.preventDefault();
                    e.stopPropagation();

                    this.app.navigateToModel(this.app, this.detailClass, this.detailNavLink, this.model);
             },
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
                     },

             addClicked: function(e) {
                console.log("add");
                e.preventDefault();
                this.app.Router.navigate("add" + firstCharUpper(this.collection.modelName), {trigger: true});
             },

             initialize: function() {
                 this.listenTo(this.collection, 'change', this._renderChildren)

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

