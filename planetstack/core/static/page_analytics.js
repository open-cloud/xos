// ----------------------------------------------------------------------------
// node count and average cpu utilization

function updatePageCPU() {
    var url="/stats/?model_name=" + admin_object_name + "&pk=" + admin_object_id + "&meter=cpu" + "&controller_name=" + admin_object_controller;
    console.log("fetching stats url " + url);
    $.ajax({
    url: url,
    dataType : 'json',
    type : 'GET',
    success: function(newData) {
        console.log(newData);
        setTimeout(updatePageAnalytics, 30000);
    },
    error: function() {
    }
});
}

$( document ).ready(function() {
    if (admin_object_name == "Sliver" && admin_object_id != undefined) {
        updatePageCPU();
    }
});

