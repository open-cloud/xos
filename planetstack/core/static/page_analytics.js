function getObjectQuery() {
    var selectedNodeTxt = $('.currentOriginalNode').text();
    selectedNodeTxt = selectedNodeTxt.trim();
    selectedNodeTxt = selectedNodeTxt.split(' ').join('');//selectedNodeTxt.replace(" ", "")
    var parentNodeTxt = $('.selectedMainNav').text();
    parentNodeTxt = parentNodeTxt.replace("/\n","");
    parentNodeTxt = parentNodeTxt.replace("»","");
    parentNodeTxt = parentNodeTxt.trim();
    if (parentNodeTxt.length > 0 && parentNodeTxt.charAt(parentNodeTxt.length-1)=='s') {
            parentNodeTxt = parentNodeTxt.substring(0, parentNodeTxt.length-1);
    }

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
    $('.'+labelName).text(legend).show();
    $('.'+valueName).text(Math.round(value)+units).show();
}

function setPageStatFloat(labelName, valueName, legend, units, value, dp) {
    $('.'+labelName).text(legend).show();
    $('.'+valueName).text(Number(value).toFixed(dp)+units).show();
}

// ----------------------------------------------------------------------------
// node count and average cpu utilization

function updatePageAnalyticsData(summaryData) {
    window.pageAnalyticsData = summaryData;
    lastRow = summaryData.rows.length-1;
    setPageStatInt("nodesLabel", "nodesValue", "Node Count", "", summaryData.rows[lastRow]["count_hostname"]);
    setPageStatInt("cpuLabel", "cpuValue", "Avg Load", "%", summaryData.rows[lastRow]["avg_cpu"]);
}

function updatePageAnalytics() {
    $.ajax({
    url : '/analytics/bigquery/?avg=%cpu&count=%hostname' + getObjectQuery(),
    dataType : 'json',
    type : 'GET',
    success: function(newData)
    {
        updatePageAnalyticsData(newData);
    }
});
    setTimeout(updatePageAnalytics, 30000);
}

setTimeout(updatePageAnalytics, 5000);

// ----------------------------------------------------------------------------
// bandwidth

function updatePageBandwidthData(summaryData) {
    window.pageBandData = summaryData;
    lastRow = summaryData.rows.length-1;
    setPageStatFloat("bandwidthLabel", "bandwidthValue", "Bandwidth", "Gbps", summaryData.rows[lastRow]["sum_computed_bytes_sent_div_elapsed"]*8.0/1024/1024/1024,2);
}

function updatePageBandwidth() {
    $.ajax({
    url : '/analytics/bigquery/?computed=%bytes_sent/%elapsed' + getObjectQuery(),
    dataType : 'json',
    type : 'GET',
    success: function(newData)
    {
        updatePageBandwidthData(newData);
    }
});
    setTimeout(updatePageBandwidth, 30000);
}

setTimeout(updatePageBandwidth, 5000);

