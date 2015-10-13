/* eslint-disable guard-for-in, no-undef, indent*/

// TODO write test and then fix lint errors

/* This is an example that uses xoslib + datatables to display the developer
   view.

   For an example that uses xoslib + marionette, see xosDeveloper.js
*/

function updateSliceTable(data) {
    $('#developerView').html('<table cellpadding="0" cellspacing="0" border="0" class="display" id="dynamicusersliceinfo"></table>');
    var actualEntries = [];

    for (rowkey in data.models) {
        row = data.models[rowkey];
        slicename = row.get('name');
        sliceid = row.get('id');
        role = row.get('sliceInfo').roles[0] || '';
        instancecount = row.get('sliceInfo').instanceCount;
        sitecount = row.get('sliceInfo').siteCount;
        backendHtml = row.get('backendHtml');

        //if (! role) {
        //    continue;
        //}

        if (! row.get('current_user_can_see')) {
            continue;
        }

        actualEntries.push([backendHtml +
            ' <a href="/admin/core/slice/' + sliceid + '">' +
            slicename + '</a>',
            role, instancecount, sitecount]);
    }
    oTable = $('#dynamicusersliceinfo').dataTable({
        'bJQueryUI': true,
        'aaData': actualEntries,
        'bStateSave': true,
        'aoColumns': [
            {'sTitle': 'Slice'},
            {'sTitle': 'Privilege' , sClass: 'alignCenter'},
            {'sTitle': 'Number of Instances' , sClass: 'alignCenter'},
            {'sTitle': 'Number of Sites' , sClass: 'alignCenter'},
        ]
    });
}

$(document).ready(function() {
    xos.slicesPlus.on('change', function() {
        updateSliceTable(xos.slicesPlus);
    });
    xos.slicesPlus.on('remove', function() {
        updateSliceTable(xos.slicesPlus);
    });
    xos.slicesPlus.on('sort', function() {
        updateSliceTable(xos.slicesPlus);
    });

    xos.slicesPlus.startPolling();
});

