// misc utility functions

function idInArray(id, arr) {
    // because sometimes ids are strings and sometimes they're integers
    for (index in arr) {
        if (id.toString() == arr[index].toString()) {
            return true;
        }
    }
    return false;
}

function assert(outcome, description) {
    if (!outcome) {
        console.log(description);
    }
}

function templateFromId(id) {
    return _.template($(id).html());
}

function firstCharUpper(s) {
    return s.charAt(0).toUpperCase() + s.slice(1);
}

function toTitleCase(str)
{
    return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}

function fieldNameToHumanReadable(str)
{
    str = str.replace("_", " ");
    return toTitleCase(str);
}

// http://stackoverflow.com/questions/2117320/set-maximum-displayed-rows-count-for-html-table
function limitTableRows(tableSelector, maxRows) {
    var table = $(tableSelector)[0] //document.getElementById(tableId);
    var wrapper = table.parentNode;
    var rowsInTable = table.rows.length;
    try {
        var border = getComputedStyle(table.rows[0].cells[0], '').getPropertyValue('border-top-width');
        border = border.replace('px', '') * 1;
    } catch (e) {
        var border = table.rows[0].cells[0].currentStyle.borderWidth;
        border = (border.replace('px', '') * 1) / 2;
    }
    var height = 0;
    if (rowsInTable > maxRows) {
        for (var i = 0; i < maxRows; i++) {
            height += table.rows[i].clientHeight + border;
            //console.log("XXX " + height + " " + table.rows[i].clientHeight + " " + border);
        }
        wrapper.style.height = height + "px";
    }
}

function validateField(validatorName, value, obj) {
    if (validatorName=="notBlank") {
        if ((value==undefined) || (value=="")) {
            return "can not be blank";
        }
    }

    // if notBlank wasn't set, and the field is blank, then we can return
    if ((value==undefined) || (value=="")) {
        return true;
    }

    switch (validatorName) {
        case "url":
            if (! /^(https?|ftp):\/\/(((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:)*@)?(((\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5]))|((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?)(:\d*)?)(\/((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)+(\/(([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)*)*)?)?(\?((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|[\uE000-\uF8FF]|\/|\?)*)?(\#((([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(%[\da-f]{2})|[!\$&'\(\)\*\+,;=]|:|@)|\/|\?)*)?$/i.test(value)) {
                return "must be a valid url";
            }
            break;

        case "portspec":
            if (! $.trim(value).match(portlist_regexp())) {
                return "must be a valid portspec (example: 'tcp 123, udp 456-789')"
            }
            break;
    }

    return true;
}

function array_diff(a1, a2)
{
  var a=[], diff=[];
  for(var i=0;i<a1.length;i++)
    a[a1[i]]=true;
  for(var i=0;i<a2.length;i++)
    if(a[a2[i]]) delete a[a2[i]];
    else a[a2[i]]=true;
  for(var k in a)
    diff.push(k);
  return diff;
}

function array_subtract(a1, a2)
{
    result=[]
    for (index in a1) {
        value = a1[index];
        if (!$.inArray(value, a2) >= 0) {
            result.push(value);
        }
    }
    return result;
}

function array_same_elements(arr1, arr2)
{
    // return true if arrays have same elements, even if order is different
    return ($(arr1).not(arr2).length == 0 && $(arr2).not(arr1).length == 0);
}

function array_pair_lookup(x, names, values)
{
    for (index in values) {
        if (values[index] == x) {
            return names[index];
        }
    }
    return "object #" + x;
}

function all_options(selector) {
    el = $(selector);
    result = [];
    _.each(el.find("option"), function(option) {
        result.push($(option).val());
    });
    return result;
}

function make_same_width(containerSelector, itemSelector) {
    var maxWidth = 0;
    $(containerSelector).find(itemSelector).each( function(index) { maxWidth = Math.max(maxWidth, $(this).width()); });
    console.log(maxWidth);
    $(containerSelector).find(itemSelector).each( function(index) { $(this).width(maxWidth); });
}

function strip_scripts(s) {
    var div = document.createElement('div');
    div.innerHTML = s;
    var scripts = div.getElementsByTagName('script');
    var i = scripts.length;
    while (i--) {
      scripts[i].parentNode.removeChild(scripts[i]);
    }
    return div.innerHTML;
  }

function parse_portlist(ports) {
    /* Support a list of ports in the format "protocol:port, protocol:port, ..."
        examples:
            tcp 123
            tcp 123:133
            tcp 123, tcp 124, tcp 125, udp 201, udp 202

        User can put either a "/" or a " " between protocol and ports
        Port ranges can be specified with "-" or ":"

        This is a straightforward port of the code in core/models/network.py
    */

    var nats = [];
    if (ports) {
        parts = ports.split(",")
        $.each(parts, function(index, part) {
            part = $.trim(part);
            if (part.indexOf("/")>=0) {
                parts2 = part.split("/",2);
                protocol=parts2[0];
                ports=parts2[1];
            } else if (part.indexOf(" ")>=0) {
                parts2 = part.split(" ",2);
                protocol=parts2[0];
                ports=parts2[1];
            } else {
                throw 'malformed port specifier ' + part + ', format example: "tcp 123, tcp 201:206, udp 333"';
            }

            protocol = $.trim(protocol);
            ports = $.trim(ports);

            if (protocol!="tcp" && protocol!="udp") {
                throw 'unknown protocol ' + protocol;
            }

            if (ports.indexOf("-")>=0) {
                parts2 = ports.split("-");
                first = parseInt($.trim(parts2[0]));
                last = parseInt($.trim(parts2[1]));
                portStr = first + ":" + last;
            } else if (ports.indexOf(":")>=0) {
                parts2 = ports.split(":");
                first = parseInt($.trim(parts2[0]));
                last = parseInt($.trim(parts2[1]));
                portStr = first + ":" + last;
            } else {
                portStr = parseInt(ports).toString();
            }

            nats.push( {l4_protocol: protocol, l4_port: portStr} );
        }); /* end $.each(ports) */
    }
    return nats
}

function portlist_regexp() {
    /* this constructs the big complicated regexp that validates port
       specifiers. Saved here in long form, in case we need to change it
       in the future.
    */

    paren = function(x) { return "(?:" + x + ")"; }
    whitespace = " *";
    protocol = paren("tcp|udp");
    protocolSlash = protocol + paren(whitespace + "|\/");
    numbers = paren("[0-9]+");
    range = paren(numbers + paren("-|:") + numbers);
    numbersOrRange = paren(numbers + "|" + range);
    protoPorts = paren(protocolSlash + numbersOrRange);
    protoPortsCommas = paren(paren(protoPorts + "," + whitespace)+"+");
    multiProtoPorts = paren(protoPortsCommas + protoPorts);
    portSpec = "^" + paren(protoPorts + "|" + multiProtoPorts) + "$";
    return RegExp(portSpec);
}

function portlist_selftest() {
    r = portlist_regexp();
    assert(! "tcp".match(r), 'should not have matched: "tcp"');
    assert("tcp 1".match(r), 'should have matched: "tcp 1"');
    assert("tcp 123".match(r), 'should have matched: "tcp 123"');
    assert("tcp  123".match(r), 'should have matched: "tcp 123"');
    assert("tcp 123-456".match(r), 'should have matched: "tcp 123-456"');
    assert("tcp 123:456".match(r), 'should have matched: "tcp 123:456"');
    assert(! "tcp 123-".match(r), 'should have matched: "tcp 123-"');
    assert(! "tcp 123:".match(r), 'should have matched: "tcp 123:"');
    assert(! "foo 123".match(r), 'should not have matched "foo 123"');
    assert("udp 123".match(r), 'should have matched: "udp 123"');
    assert("tcp 123,udp 456".match(r), 'should have matched: "tcp 123,udp 456"');
    assert("tcp 123, udp 456".match(r), 'should have matched: "tcp 123, udp 456"');
    assert("tcp 123,  udp 456".match(r), 'should have matched: "tcp 123,  udp 456"');
    assert("tcp 123-45, udp 456".match(r), 'should have matched: "tcp 123-45, udp 456"');
    assert("tcp 123-45, udp 456, tcp 11, tcp 22:45, udp 76, udp 47:49, udp 60-61".match(r), 'should have matched: "tcp 123-45, udp 456, tcp 11, tcp 22:45, udp 76, udp 47:49, udp 60-61"');
    return "done";
}

//portlist_selftest();


