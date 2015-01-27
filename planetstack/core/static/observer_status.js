function updateObserverStatus() {
    var url="/observer";
    console.log("fetching observer status url " + url);
    $.ajax({ url: url,
             dataType : 'json',
             type : 'GET',
             success: function(newData) {
                  console.log(newData);
                  if (newData.health==":-)") {
                      html = '<span style="margin-left: 16px;" title="last observer run time = ' + Math.floor(newData.last_duration) + ' seconds"><img src="/static/img/green-cloud.gif" width=16 height=16></span>';
                  } else {
                      html = '<span style="margin-left: 16px;" title="observer is offline"><img src="/static/img/red-cloud.gif"></span>';
                  }
                  $("#observer-status").html(html);
                  setTimeout(function() { updateObserverStatus(); }, 60000);
             },
             error: function() {
                  setTimeout(function() { updateObserverStatus(); }, 60000);
             }
});
}

$( document ).ready(function() {
    updateObserverStatus();
});
