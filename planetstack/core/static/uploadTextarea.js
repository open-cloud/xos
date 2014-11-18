function uploadTextarea(event,textarea_id) {
    var input = event.target;

    var reader = new FileReader();
    //reader.onloadstart = function() {
    //	reader.abort();
    //};

    reader.onloadend = function() {
        if (reader.error) {
   	    alert(reader.error.message);
        } else {
            $("#" + textarea_id).val(this.result);
	    //console.log(this.result);
        }
    };

    reader.readAsText(input.files[0]);
};
