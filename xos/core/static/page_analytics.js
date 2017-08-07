
/*
 * Copyright 2017-present Open Networking Foundation

 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at

 * http://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


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

