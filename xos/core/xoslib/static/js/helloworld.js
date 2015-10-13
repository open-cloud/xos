/* eslint-disable guard-for-in */

// helloworld.js
function updateHelloWorldData() {
  var html = '<table class="table table-bordered table-striped">';

  for (var slicekey in xos.slices.models) {
    var slice = xos.slices.models[slicekey];

    html = html + '<tr><td>' + slice.get('name') + '</td><td>' + slice.get('description') + '</td></tr>';
  }
  html = html + '</table>';
  $('#dynamicTableOfInterestingThings').html(html);
}

$(document).ready(function() {
  xos.slices.on('change', function() {
    updateHelloWorldData();
  });
  xos.slices.on('remove', function() {
    updateHelloWorldData();
  });
  xos.slices.on('sort', function() {
    updateHelloWorldData();
  });

  xos.slices.startPolling();
});

// helloworld.js
$(document).ready(function() {
  $('#submitNewDescription').bind('click', function() {
    var newDescription = $('#newDescription').val();

    xos.slices.models[0].set('description', newDescription);
    xos.slices.models[0].save();
  });
});
