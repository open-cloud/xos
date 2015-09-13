// ----------------------------------------------------------------------------
// node count and average cpu utilization

function updateMiniDashStatistic(meter, buttonSelector) {
    var url="/stats/?model_name=" + admin_object_name + "&pk=" + admin_object_id + "&meter=" + meter + "&controller_name=" + admin_object_controller;
    console.log("fetching stats url " + url);
    $.ajax({
    url: url,
    dataType : 'json',
    type : 'GET',
    success: function(newData) {
        console.log(newData);
        if (newData.error) {
            $(buttonSelector).text(newData.error);
        } else if (newData.stat_list.length > 0) {
            value = newData.stat_list.slice(-1)[0].value;
            console.log(value);
            $(buttonSelector).text(Math.round(value)).show();
        } else {
            $(buttonSelector).text("no data").show();
        }
        setTimeout(function() { updateMiniDashStatistic(meter, buttonSelector); }, 30000);
    },
    error: function() {
    }
});
}

$( document ).ready(function() {
    if (admin_object_name == "Instance" && admin_object_id != undefined) {
        updateMiniDashStatistic("cpu", "#miniDashCPU");
        updateMiniDashStatistic("network.outgoing.bytes", "#miniDashBandwidthIn");
        updateMiniDashStatistic("network.incoming.bytes", "#miniDashBandwidthOut");
    }
});

