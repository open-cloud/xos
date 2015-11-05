/* eslint-disable */
SC_HPC_FETCH = 3600;

var hpc_data = null;

function updateHpcUrlTable() {
    hpcnode = null;
    selected_node_name = $("#xos-hpc-node-select").val();

    for (index in hpc_data) {
        if (hpc_data[index].name == selected_node_name) {
            hpcnode = hpc_data[index];
        };
    }

    if (hpcnode == null) {
       $("#xos-hpc-urls").html("select a node");
       return;
    }

    $('#xos-hpc-urls').html( '<table cellpadding="0" cellspacing="0" border="0" class="display" id="dynamic_hpc_urls"></table>' );
    var actualEntries = [];

    if (parseInt(hpcnode["watcher.HPC-fetch.time"])> SC_HPC_FETCH) {
        $("#xos-hpc-urls").html("stale");
        return;
    }

    urls = hpcnode["watcher.HPC-fetch.urls"];

    for (index in urls) {
        url = urls[index];
        bytes_downloaded=url[2];
        total_time = url[3];
        if (total_time > 0) {
            KBps = Math.round(bytes_downloaded/total_time/1024.0);
        } else {
            KBps = 0;
        }
        actualEntries.push( [url[0], url[1], bytes_downloaded, total_time, KBps] );
    }

    oTable = $('#dynamic_hpc_urls').dataTable( {
        "bJQueryUI": true,
        "aaData":  actualEntries ,
        "bStateSave": true,
        "bFilter": false,
        "bPaginate": false,
        "aoColumns": [
            { "sTitle": "Url", },
            { "sTitle": "Status" },
            { "sTitle": "Bytes_Downloaded" },
            { "sTitle": "Total_Time" },
            { "sTitle": "KBps" },
        ]
    } );
}

function updateNodeList() {
    selected_node_name = $("#xos-hpc-node-select").val();

    options = [];
    for (index in hpc_data) {
        node = hpc_data[index];
        if (node.name == selected_node_name) {
            options.push("<option value=\"" + node.name + "\" selected>" + node.name + "</option>");
        } else {
            options.push("<option value=\"" + node.name + "\">" + node.name + "</option>");
        }
    }

    $("#xos-hpc-node-select").html(options);
}

function updateHpcView(data) {
    data = data[0];
    hpc_data = data.attributes.hpc;
    updateNodeList();
    updateHpcUrlTable();
}

$(document).ready(function(){
    xos.hpcview.on("change", function() { console.log("change"); updateHpcView(xos.hpcview.models); });
    xos.hpcview.on("remove", function() { console.log("sort"); updateHpcView(xos.hpcview.models); });
    xos.hpcview.on("sort", function() { console.log("sort"); updateHpcView(xos.hpcview.models); });

    $("#xos-hpc-node-select").click( function() { updateHpcUrlTable(); } );

    xos.hpcview.startPolling();
});

/* eslint-enable */
