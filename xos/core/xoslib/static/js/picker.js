function init_picker(selector, ordered) {
  //console.log("init_picker");
  //console.log($(selector));

  var addBtn = $(selector).find('.btn-picker-add');
  var removeBtn = $(selector).find('.btn-picker-remove');
  var upBtn = $(selector).find('.btn-picker-up');
  var downBtn = $(selector).find('.btn-picker-down');
  var from = $(selector).find('.select-picker-from');
  var to = $(selector).find('.select-picker-to');

  if (!ordered) {
    upBtn.hide();
    downBtn.hide();
  }

  addBtn.click(function() {
    from.find(':selected').each(function() {
      to.append('<option value="' + $(this).val() + '"">' + $(this).text() + '</option>');
      $(this).remove();
    });
  });
  removeBtn.click(function() {
    to.find(':selected').each(function() {
      from.append('<option value="' + $(this).val() + '">' + $(this).text() + '</option>');
      $(this).remove();
    });
  });
  upBtn.bind('click', function() {
    to.find(':selected').each(function() {
      var newPos = to.find('option').index(this) - 1;

      if (newPos > -1) {
        to.find('option').eq(newPos).before('<option value="' + $(this).val() + '" selected="selected">' + $(this).text() + '</option>');
        $(this).remove();
      }
    });
  });
  downBtn.bind('click', function() {
    var countOptions = to.find('option').size();

    to.find(':selected').each(function() {
      var newPos = to.find('option').index(this) + 1;

      if (newPos < countOptions) {
        to.find('option').eq(newPos).after('<option value="' + $(this).val() + '" selected="selected">' + $(this).text() + '</option>');
        $(this).remove();
      }
    });
  });
};

function init_spinner(selector, value) {
  $(selector).spinner('value', value);
};
