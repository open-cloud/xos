SC_RR = 60;
SC_HPC_PROBE = 600;
SC_HPC_FETCH = 3600;

function staleCheck(row, time_key, msg_key, seconds) {
    if (parseInt(row[time_key])>seconds) {
        return "stale";
    } else {
        if (! row[msg_key]) {
            return "null";
        } else {
            return row[msg_key];
        }
    }
}

function updateDnsDemuxTable(dnsdemux) {
    $('#xos-hpc-dns').html( '<table cellpadding="0" cellspacing="0" border="0" class="display" id="dynamic_dnsdemux"></table>' );
    var actualEntries = [];

    console.log(dnsdemux);

    for (rowkey in dnsdemux) {
        row = dnsdemux[rowkey];

        actualEntries.push( [row.name, row.ip, staleCheck(row, "watcher.DNS.time", "watcher.DNS.msg", SC_RR)] );
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
            { "sTitle": "Record Checker" },
        ]
    } );
}

function updateHpcTable(dnsdemux) {
    $('#xos-hpc-hpc').html( '<table cellpadding="0" cellspacing="0" border="0" class="display" id="dynamic_hpc"></table>' );
    var actualEntries = [];

    console.log(dnsdemux);

    for (rowkey in dnsdemux) {
        row = dnsdemux[rowkey];

        actualEntries.push( [row.name, staleCheck(row, "watcher.HPC-hb.time", "watcher.HPC-hb.msg", SC_HPC_PROBE), staleCheck(row, "watcher.HPC-fetch.time", "watcher.HPC-fetch.msg", SC_HPC_FETCH) ] );
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
            { "sTitle": "Prober" },
            { "sTitle": "Fetcher" },
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


