/* eslint-disable */
SC_HPC_FETCH = 3600;

var hpc_data = null;

function updateHpcUrlTable() {
    hpcnode = null;
    selected_url = $("#xos-hpc-url-select").val();

    $('#xos-hpc-urls').html( '<table cellpadding="0" cellspacing="0" border="0" class="display" id="dynamic_hpc_urls"></table>' );
    var actualEntries = [];

    for (index in hpc_data) {
        hpc_node = hpc_data[index];

        if (parseInt(hpc_node["watcher.HPC-fetch.time"]) > SC_HPC_FETCH) {
            $("#xos-hpc-urls").html("stale");
            actualEntries.push( [hpc_node.name, "stale", "stale", "stale", "stale"] );
        } else {
            urls = hpc_node["watcher.HPC-fetch.urls"];

            found = null;
            for (j in urls) {
                url = urls[j];

                if (url[0] == selected_url) {
                    found = url;
                }
            }

            if (found==null) {
                actualEntries.push( [hpc_node.name, "not found", "not found", "not found", "not found"] );
            } else {
                bytes_downloaded=url[2];
                total_time = url[3];
                if (total_time > 0) {
                    KBps = Math.round(bytes_downloaded/total_time/1024.0);
                } else {
                    KBps = 0;
                }
                actualEntries.push( [hpc_node.name, url[1], bytes_downloaded, total_time, KBps] );
            }
        }
    }

    oTable = $('#dynamic_hpc_urls').dataTable( {
        "bJQueryUI": true,
        "aaData":  actualEntries ,
        "bStateSave": true,
        "bFilter": false,
        "bPaginate": false,
        "aoColumns": [
            { "sTitle": "Node", },
            { "sTitle": "Status" },
            { "sTitle": "Bytes_Downloaded" },
            { "sTitle": "Total_Time" },
            { "sTitle": "KBps" },
        ]
    } );
}

function updateUrlList() {
    selected_url = $("#xos-hpc-url-select").val();

    urls = [];
    for (index in hpc_data) {
        node = hpc_data[index];
        node_urls = node["watcher.HPC-fetch.urls"];
        for (j in node_urls) {
            url = node_urls[j][0];
            if ($.inArray(url, urls) < 0) {
                urls.push(url);
            }
        }
    }

    console.log(urls);

    options = [];
    for (index in urls) {
        url = urls[index];
        if (node.name == selected_url) {
            options.push("<option value=\"" + url + "\" selected>" + url + "</option>");
        } else {
            options.push("<option value=\"" + url + "\">" + url + "</option>");
        }
    }

    $("#xos-hpc-url-select").html(options);
}

function updateHpcView(data) {
    data = data[0];
    hpc_data = data.attributes.hpc;
    updateUrlList();
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

