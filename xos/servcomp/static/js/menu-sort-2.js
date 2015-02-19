jQuery(function($) {
    $("div.inline-group").sortable({ 
        axis: 'y',
        placeholder: 'ui-state-highlight', 
        forcePlaceholderSize: 'true', 
        items: '.row1, .row2', 
        update: update
    });
    $("div.inline-group").disableSelection();
});
function update() {
    $('.row1, .row2').each(function(i) {
        $(this).find('input[id$=order]').val(i+1);
    });
}
jQuery(document).ready(function($){
//    $(this).find('input[id$=order]').parent('div').parent('div').hide().parent().parent().css('cursor','move');
    $(this).find('input[id$=order]').parent('td').hide().parent('tr').parent('tbody').parent('table').find("th:contains('Order')").hide(); 
    $(this).find('input[id$=order]').parent('td').hide().parent('tr').parent('tbody').parent('table').css('cursor','move');
    $('.add-row a').click(update);
});
