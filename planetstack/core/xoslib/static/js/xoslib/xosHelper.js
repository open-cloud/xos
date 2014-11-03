XOSApplication = Marionette.Application.extend({
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

