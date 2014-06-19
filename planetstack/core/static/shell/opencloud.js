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

function OpenCloudModel(name) {
    this.all = function() { return opencloud_data[name]; };

    this.match = function(filterDict,obj) {
                   for (var k in filterDict) {
                       if (obj[k] == filterDict[k]) {
                           return true;
                       }
                   }
                   return false;
                 };

    this.filter = function(filterDict) {
                   result = []
                   all_objs = this.all()
                   for (var k in all_objs) {
                        obj = all_objs[k];
                        if (this.match(filterDict, obj)) {
                            result.push(obj);
                        }
                   }
                   return result;
                 };

    this.get = function(filterDict) {
                   return this.filter(filterDict)[0];
                 };

    this.__str__ = function() { return '["all", "filter", "get"]' };
}

//function Slices() {
//    this.listAll = function() { return opencloud_data["slices"] }
//    this.__str__ = function() { return '["listAll"]'; }
//}

function OpenCloud() {
    this.slices = new OpenCloudModel("slices");
    this.slivers = new OpenCloudModel("slivers");
    this.nodes = new OpenCloudModel("nodes");
    this.sites = new OpenCloudModel("sites");
    this.__str__ = function() { return '["slices", "slivers", "nodes", "sites"]'; }
};
