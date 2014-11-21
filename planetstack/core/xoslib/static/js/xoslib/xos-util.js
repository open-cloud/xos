// misc utility functions

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
