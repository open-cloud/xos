// misc utility functions

function idInArray(id, arr) {
    // because sometimes ids are strings and sometimes they're integers
    for (index in arr) {
        if (id.toString() == arr[index].toString()) {
            return true;
        }
    }
    return false;
}

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

function toTitleCase(str)
{
    return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}

function fieldNameToHumanReadable(str)
{
    str = str.replace("_", " ");
    return toTitleCase(str);
}

// http://stackoverflow.com/questions/2117320/set-maximum-displayed-rows-count-for-html-table
function limitTableRows(tableSelector, maxRows) {
    var table = $(tableSelector)[0] //document.getElementById(tableId);
    var wrapper = table.parentNode;
    var rowsInTable = table.rows.length;
    try {
        var border = getComputedStyle(table.rows[0].cells[0], '').getPropertyValue('border-top-width');
        border = border.replace('px', '') * 1;
    } catch (e) {
        var border = table.rows[0].cells[0].currentStyle.borderWidth;
        border = (border.replace('px', '') * 1) / 2;
    }
    var height = 0;
    if (rowsInTable > maxRows) {
        for (var i = 0; i < maxRows; i++) {
            height += table.rows[i].clientHeight + border;
            //console.log("XXX " + height + " " + table.rows[i].clientHeight + " " + border);
        }
        wrapper.style.height = height + "px";
    }
}

function validateField(validatorName, value, obj) {
    if (validatorName=="notBlank") {
        if ((value==undefined) || (value=="")) {
            return "can not be blank";
        }
    }

    // if notBlank wasn't set, and the field is blank, then we can return
    if ((value==undefined) || (value=="")) {
        return true;
    }

    switch (validatorName) {
        case "url":
            if (! /^(https?|ftp):\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(\#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i.test(value)) {
                return "must be a valid url";
            }
            break;
    }

    return true;
}
