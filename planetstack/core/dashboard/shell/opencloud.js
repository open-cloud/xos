var opencloud_data = [];
var opencloud_data_received = false;

function updateOpenCloud(onLoaded) {
    $.ajax({url: "/admin/shelldata",
        dataType: "json",
        type: "GET",
        success: function(data) {
            opencloud_data = data;
            if (!opencloud_data_received) {
                opencloud_data_received = true;
                if (onLoaded!=null) {
                    onLoaded();
                }
            }
            // do this again in 30 seconds
            setTimeout(function() {updateOpenCloud(onLoaded)}, 10000);
        },
        error: function() {
            console.log("something went wrong. trying again");
            // do this again in 30 seconds
            setTimeout(function() {updateOpenCloud(onLoaded)}, 10000);
        }
    });
}

function Slices() {
    this.listAll = function() { return opencloud_data["slices"] }
    this.__str__ = function() { return '["listAll"]'; }
}

function OpenCloud() {
    this.slices = new Slices()
    this.__str__ = function() { return '["slices"]'; }
};
