XOSApplication = Marionette.Application.extend({
    detailBoxId: "#detailBox",
    errorBoxId: "#errorBox",
    errorCloseButtonId: "#close-error-box",
    successBoxId: "#successBox",
    successCloseButtonId: "#close-success-box",
    errorTemplate: "#xos-error-template",
    successTemplate: "#xos-success-template",

    hideError: function(result) {
        $(this.errorBoxId).hide();
        $(this.successBoxId).hide();
    },

    showSuccess: function(result) {
         $(this.successBoxId).show();
         $(this.successBoxId).html(_.template($(this.successTemplate).html())(result));
         $(this.successCloseButtonId).unbind().bind('click', function() {
             $(this.successBoxId).hide();
         });
    },

    showError: function(result) {
         $(this.errorBoxId).show();
         $(this.errorBoxId).html(_.template($(this.errorTemplate).html())(result));
         $(this.errorCloseButtonId).unbind().bind('click', function() {
             $(this.errorBoxId).hide();
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

            events: {"click button.js-submit": "submitClicked",
                     "change input": "inputChanged"},

            events: {"click button.js-submit": "submitClicked",
                     "change input": "inputChanged"},

            /* inputChanged is watching the onChange events of the input controls. We
               do this to track when this view is 'dirty', so we can throw up a warning
               if the user tries to change his slices without saving first.
            */

            inputChanged: function(e) {
                this.dirty = true;
            },

            saveError: function(model, result, xhr) {
                this.app.showError(result);
            },

            saveSuccess: function(model, result, xhr) {
                this.app.showSuccess({status: xhr.xhr.status, statusText: xhr.xhr.statusText});
            },

            submitClicked: function(e) {
                this.app.hideError();
                e.preventDefault();
                var data = Backbone.Syphon.serialize(this);
                var thisView = this;
                this.model.save(data, {error: function(model, result, xhr) { thisView.saveError(model, result, xhr); },
                                       success: function(model, result, xhr) { thisView.saveSuccess(model, result, xhr); }});
                this.dirty = false;
            },

            showLinkedItems: function() {
                    index=0;
                    for (relatedName in this.model.collection.relatedCollections) {
                        relatedField = this.model.collection.relatedCollections[relatedName];

                        relatedListViewClassName = relatedName + "ListView";
                        if (this.app[relatedListViewClassName] == undefined) {
                            console.log("warning: " + relatedListViewClassName + " not found");
                        }
                        relatedListViewClass = this.app[relatedListViewClassName].extend({collection: xos[relatedName].filterBy(relatedField,this.model.id)});
                        this.app["linkedObjs" + (index+1)].show(new relatedListViewClass());
                        index = index + 1;
                    }

                    while (index<4) {
                        this.app["linkedObjs" + (index+1)].empty();
                        index = index + 1;
                    }
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

