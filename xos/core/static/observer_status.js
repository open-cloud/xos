function updateObserverStatus() {
    var url="/observer";
    $.ajax({ url: url,
             dataType : 'json',
             type : 'GET',
             success: function(newData) {
                  console.log(newData);
                  if (newData.health==":-)") {
                      tooltip = 'last synchronizer run time = ' + Math.floor(newData.last_duration) + ' seconds';
                      icon = "/static/img/green-cloud.gif";
                  } else {
                      tooltip = "synchronizer is offline";
                      icon = "/static/img/red-cloud.gif";
                  }

                  html = '<span style="margin-left: 16px; cursor: pointer;" title="' + tooltip + '"><img src="' + icon +
                         '" width=16 height=16 onClick="showObserverCalendar();"></span>';

                  $("#observer-status").html(html);
                  setTimeout(function() { updateObserverStatus(); }, 60000);
             },
             error: function() {
                  setTimeout(function() { updateObserverStatus(); }, 60000);
             }
});
}

function showObserverCalendar() {
    $("#dialog-placeholder").html('<iframe src="https://www.google.com/calendar/embed?src=qlnr1b3rsquq702nbns42l88s4%40group.calendar.google.com&ctz=America/New_York" style="border: 0" width="800" height="600" frameborder="0" scrolling="no"></iframe>');
    $("#dialog-placeholder").dialog({
           autoOpen: false,
           modal: true,
           width: 850,
           buttons : {
                "Ok" : function() {
                  $(this).dialog("close");
                }
              }
            });
        $("#dialog-placeholder").dialog("open");
}

$( document ).ready(function() {
    updateObserverStatus();
});
