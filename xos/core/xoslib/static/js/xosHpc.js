function staleCheck(row, time_key, msg_key) {
    if (parseInt(row[time_key])>30) {
        return "stale";
    } else {
        return row[msg_key];
    }
}

function updateDnsDemuxTable(dnsdemux) {
    $('#xos-hpc-dns').html( '<table cellpadding="0" cellspacing="0" border="0" class="display" id="dynamic_dnsdemux"></table>' );
    var actualEntries = [];

    console.log(dnsdemux);

    for (rowkey in dnsdemux) {
        row = dnsdemux[rowkey];

        actualEntries.push( [row.name, row.ip, staleCheck(row, "watcher.DNS.time", "watcher.DNS.msg")] );
    }
    console.log(actualEntries);
    oTable = $('#dynamic_dnsdemux').dataTable( {
        "bJQueryUI": true,
        "aaData":  actualEntries ,
        "bStateSave": true,
        "bFilter": false,
        "bPaginate": false,
        "aoColumns": [
            { "sTitle": "Node" },
            { "sTitle": "IP Address" },
            { "sTitle": "Status" },
        ]
    } );
}

function updateHpcTable(dnsdemux) {
    $('#xos-hpc-hpc').html( '<table cellpadding="0" cellspacing="0" border="0" class="display" id="dynamic_hpc"></table>' );
    var actualEntries = [];

    console.log(dnsdemux);

    for (rowkey in dnsdemux) {
        row = dnsdemux[rowkey];

        actualEntries.push( [row.name, staleCheck(row, "watcher.HPC-hb.time", "watcher.HPC-hb.msg")] );
    }
    console.log(actualEntries);
    oTable = $('#dynamic_hpc').dataTable( {
        "bJQueryUI": true,
        "aaData":  actualEntries ,
        "bStateSave": true,
        "bFilter": false,
        "bPaginate": false,
        "aoColumns": [
            { "sTitle": "Node", },
            { "sTitle": "Status" },
        ]
    } );
}

function updateHpcView(data) {
    data = data[0];
    updateDnsDemuxTable( data.attributes.dnsdemux );
    updateHpcTable( data.attributes.hpc );
}

$(document).ready(function(){
    xos.hpcview.on("change", function() { console.log("change"); updateHpcView(xos.hpcview.models); });
    xos.hpcview.on("remove", function() { console.log("sort"); updateHpcView(xos.hpcview.models); });
    xos.hpcview.on("sort", function() { console.log("sort"); updateHpcView(xos.hpcview.models); });

    xos.hpcview.startPolling();
});


