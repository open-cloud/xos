function getPageKind() {
    var parentNodeTxt = $('#selectedMainNav').text();
    parentNodeTxt = parentNodeTxt.replace("/\n","");
    parentNodeTxt = parentNodeTxt.replace("»","");
    parentNodeTxt = parentNodeTxt.trim();
    if (parentNodeTxt.length > 0 && parentNodeTxt.charAt(parentNodeTxt.length-1)=='s') {
            parentNodeTxt = parentNodeTxt.substring(0, parentNodeTxt.length-1);
    }
    return parentNodeTxt;
}

function getObjectQuery() {
    var selectedNodeTxt = $('#currentOriginalNode').text();
    selectedNodeTxt = selectedNodeTxt.trim();
    selectedNodeTxt = selectedNodeTxt.split(' ').join('');//selectedNodeTxt.replace(" ", "")
    parentNodeTxt = getPageKind();

    if (parentNodeTxt == "Slice") {
        return "&slice=" + selectedNodeTxt;
    } else if (parentNodeTxt == "Site") {
        return "&site=" + selectedNodeTxt;
    } else if (parentNodeTxt == "Node") {
        return "&node=" + selectedNodeTxt;
    } else {
        return "";
    }
}


function setPageStatInt(labelName, valueName, legend, units, value) {
    $(labelName).text(legend).show();
    $(valueName).text(Math.round(value)+units).show();
}

function setPageStatFloat(labelName, valueName, legend, units, value, dp) {
    $(labelName).text(legend).show();
    $(valueName).text(Number(value).toFixed(dp)+units).show();
}

// ----------------------------------------------------------------------------
// node count and average cpu utilization

function updatePageAnalyticsData(summaryData) {
    window.pageAnalyticsUrl = summaryData["dataSourceUrl"];
    lastRow = summaryData.rows.length-1;

    if (summaryData.msg) {
        $("#minidashStatus").text(summaryData.msg).show();
    } else {
        $("#minidashStatus").text("").hide();
    }

    if (summaryData.rows.length <= 0) {
        //console.log("no data received from page analytics ajax")
        return;
    }

    //Old minidashboard
    //setPageStatInt(".nodesLabel", ".nodesValue", "Node Count", "", summaryData.rows[lastRow]["count_hostname"]);
    //setPageStatInt(".cpuLabel", ".cpuValue", "Avg Load", "%", summaryData.rows[lastRow]["avg_cpu"]);

    //New miniDashboard
    setPageStatInt("#miniDashNodeCountLabel", "#miniDashNodeCount", "Node Count", "", summaryData.rows[lastRow]["count_hostname"]);
    setPageStatInt("#miniDashAvgLoadLabel", "#miniDashAvgLoad", "Avg Load", "%", summaryData.rows[lastRow]["avg_cpu"]);
}

function updatePageAnalytics() {
    var url= '/analytics/bigquery/?avg=%cpu&count=%hostname&cached=default' + getObjectQuery();
    $.ajax({
    url: url,
    dataType : 'json',
    type : 'GET',
    success: function(newData) {
        updatePageAnalyticsData(newData);
        setTimeout(updatePageAnalytics, 30000);
    },
    error: function() {
        console.log("error retrieving statistics; retry in 5 seconds");
        setTimeout(updatePageBandwidth, 5000);
    }
});
}

// ----------------------------------------------------------------------------
// bandwidth

function updatePageBandwidthData(summaryData) {
    window.pageBandwidthUrl = summaryData["dataSourceUrl"];
    lastRow = summaryData.rows.length-1;

    if (summaryData.rows.length <= 0) {
        //console.log("no data received from page bandwidth ajax")
        return;
    }

    //Old minidashboard
    //setPageStatFloat(".bandwidthLabel", ".bandwidthValue", "Bandwidth", " Gbps", summaryData.rows[lastRow]["sum_computed_bytes_sent_div_elapsed"]*8.0/1024/1024/1024,2);

    //New minidashboard
    setPageStatFloat("#miniDashBandwidthLabel", "#miniDashBandwidth", "Bandwidth", " Gbps", summaryData.rows[lastRow]["sum_computed_bytes_sent_div_elapsed"]*8.0/1024/1024/1024,2);
}

function updatePageBandwidth() {
    var url='/analytics/bigquery/?computed=%bytes_sent/%elapsed&cached=default' + getObjectQuery();

    if (getPageKind()!="Slice") {
        url = url + "&event=node_heartbeat";
    }

    $.ajax({
    url : url,
    dataType : 'json',
    type : 'GET',
    success: function(newData) {
        updatePageBandwidthData(newData);
        setTimeout(updatePageBandwidth, 30000);
    },
    error: function() {
        console.log("error retrieving statistics; retry in 5 seconds")
        setTimeout(updatePageBandwidth, 5000);
    }
});
}

$( document ).ready(function() {
    updatePageAnalytics();
    updatePageBandwidth();
});

