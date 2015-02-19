DB = function() {
}

print = function(msg) {
  //console.log(msg);
}


friendlyEqual = function( a , b ){
    if ( a == b )
        return true;

    if ( tojson( a ) == tojson( b ) )
        return true;

    return false;
}


doassert = function( msg ){
    print( "assert: " + msg );
    throw msg;
}

assert = function( b , msg ){
    if ( assert._debug && msg ) print( "in assert for: " + msg );

    if ( b )
        return;
    
    doassert( "assert failed : " + msg );
}

assert.eq = function( a , b , msg ){
    if ( assert._debug && msg ) print( "in assert for: " + msg );

    if ( a == b )
        return;

    if ( ( a != null && b != null ) && friendlyEqual( a , b ) )
        return;

    doassert( "[" + tojson( a ) + "] != [" + tojson( b ) + "] are not equal : " + msg );
}

assert.neq = function( a , b , msg ){
    if ( assert._debug && msg ) print( "in assert for: " + msg );
    if ( a != b )
        return;

    doassert( "[" + a + "] != [" + b + "] are equal : " + msg );
}

assert.soon = function( f, msg, timeout, interval ) {
    if ( assert._debug && msg ) print( "in assert for: " + msg );

    var start = new Date();
    timeout = timeout || 30000;
    interval = interval || 200;
    var last;
    while( 1 ) {
        
        if ( typeof( f ) == "string" ){
            if ( eval( f ) )
                return;
        }
        else {
            if ( f() )
                return;
        }
        
        if ( ( new Date() ).getTime() - start.getTime() > timeout )
            doassert( "assert.soon failed: " + f + ", msg:" + msg );
        sleep( interval );
    }
}

assert.throws = function( func , params , msg ){
    if ( assert._debug && msg ) print( "in assert for: " + msg );
    try {
        func.apply( null , params );
    }
    catch ( e ){
        return e;
    }

    doassert( "did not throw exception: " + msg );
}

assert.commandWorked = function( res , msg ){
    if ( assert._debug && msg ) print( "in assert for: " + msg );

    if ( res.ok == 1 )
        return;
    
    doassert( "command failed: " + tojson( res ) + " : " + msg );
}

assert.commandFailed = function( res , msg ){
    if ( assert._debug && msg ) print( "in assert for: " + msg );

    if ( res.ok == 0 )
        return;
    
    doassert( "command worked when it should have failed: " + tojson( res ) + " : " + msg );
}

assert.isnull = function( what , msg ){
    if ( assert._debug && msg ) print( "in assert for: " + msg );

    if ( what == null )
        return;
    
    doassert( "supposed to null (" + ( msg || "" ) + ") was: " + tojson( what ) );
}

assert.lt = function( a , b , msg ){
    if ( assert._debug && msg ) print( "in assert for: " + msg );

    if ( a < b )
        return;
    doassert( a + " is not less than " + b + " : " + msg );
}

assert.gt = function( a , b , msg ){
    if ( assert._debug && msg ) print( "in assert for: " + msg );

    if ( a > b )
        return;
    doassert( a + " is not greater than " + b + " : " + msg );
}

Object.extend = function( dst , src , deep ){
    for ( var k in src ){
        var v = src[k];
        if ( deep && typeof(v) == "object" ){
            v = Object.extend( typeof ( v.length ) == "number" ? [] : {} , v , true );
        }
        dst[k] = v;
    }
    return dst;
}

argumentsToArray = function( a ){
    var arr = [];
    for ( var i=0; i<a.length; i++ )
        arr[i] = a[i];
    return arr;
}

isString = function( x ){
    return typeof( x ) == "string";
}

isNumber = function(x){
    return typeof( x ) == "number";
}

isObject = function( x ){
    return typeof( x ) == "object";
}

String.prototype.trim = function() {
    return this.replace(/^\s+|\s+$/g,"");
}
String.prototype.ltrim = function() {
    return this.replace(/^\s+/,"");
}
String.prototype.rtrim = function() {
    return this.replace(/\s+$/,"");
}

Date.timeFunc = function( theFunc , numTimes ){

    var start = new Date();
    
    numTimes = numTimes || 1;
    for ( var i=0; i<numTimes; i++ ){
        theFunc.apply( null , argumentsToArray( arguments ).slice( 2 ) );
    }

    return (new Date()).getTime() - start.getTime();
}

Date.prototype.tojson = function(){
    return "\"" + this.toString() + "\"";
}

RegExp.prototype.tojson = RegExp.prototype.toString;

Array.contains = function( a  , x ){
    for ( var i=0; i<a.length; i++ ){
        if ( a[i] == x )
            return true;
    }
    return false;
}

Array.unique = function( a ){
    var u = [];
    for ( var i=0; i<a.length; i++){
        var o = a[i];
        if ( ! Array.contains( u , o ) ){
            u.push( o );
        }
    }
    return u;
}

Array.shuffle = function( arr ){
    for ( var i=0; i<arr.length-1; i++ ){
        var pos = i+Math.floor(Math.random()*(arr.length-i));
        var save = arr[i];
        arr[i] = arr[pos];
        arr[pos] = save;
    }
    return arr;
}


Array.tojson = function( a , indent , x , html){
    if (!indent) 
        indent = "";
    var spacer = "";
    if(html) {
      spacer = "<br/>";
      indent = " &nbsp; "
    }

    var s = spacer + "[ " + spacer;
    indent += " ";
    for ( var i=0; i<a.length; i++){
        s += indent + tojson( a[i], indent );
        if ( i < a.length - 1 ){
            s += "," + spacer;
        }
    }
    if ( a.length == 0 ) {
        s += indent;
    }

    indent = indent.substring(1);
    s += spacer + " "+"]";
    return s;
}

Array.fetchRefs = function( arr , coll ){
    var n = [];
    for ( var i=0; i<arr.length; i ++){
        var z = arr[i];
        if ( coll && coll != z.getCollection() )
            continue;
        n.push( z.fetch() );
    }
    
    return n;
}

Array.sum = function( arr ){
    if ( arr.length == 0 )
        return null;
    var s = arr[0];
    for ( var i=1; i<arr.length; i++ )
        s += arr[i];
    return s;
}

Array.avg = function( arr ){
    if ( arr.length == 0 )
        return null;
    return Array.sum( arr ) / arr.length;
}

Array.stdDev = function( arr ){
    var avg = Array.avg( arr );
    var sum = 0;

    for ( var i=0; i<arr.length; i++ ){
        sum += Math.pow( arr[i] - avg , 2 );
    }

    return Math.sqrt( sum / arr.length );
}

if ( ! ObjectId.prototype )
    ObjectId.prototype = {}

ObjectId.prototype.toString = function(){
    return this.str;
}

ObjectId.prototype.tojson = function(){
    return "ObjectId(\"" + this.str + "\")";
}

ObjectId.prototype.isObjectId = true;

tojson = function( x, indent , nolint , html){
    if ( x == null )
        return "null";
    
    if ( x == undefined )
        return "undefined";
    
    if (!indent) 
        indent = "";

    switch ( typeof x ){
        
    case "string": {
        var s = "\"";
        for ( var i=0; i<x.length; i++ ){
            if ( x[i] == '"' ){
                s += "\\\"";
            }
            else
                s += x[i];
        }
        return s + "\"";
    }
        
    case "number": 
    case "boolean":
        return "" + x;
            
    case "object":{
        var s = tojsonObject( x, indent , nolint , html);
        if ( ( nolint == null || nolint == true ) && s.length < 80 && ( indent == null || indent.length == 0 ) ){
            s = s.replace( /[\s\r\n ]+/gm , " " );
        }
        return s;
    }
        
    case "function":
        return x.toString();
        

    default:
        throw "tojson can't handle type " + ( typeof x );
    }
    
}

tojsonObject = function( x, indent , nolint , html){
    if(html) {
      var lineEnding = "<br/>";
      var tabSpace   = "&nbsp;";
    }
    else {
      var lineEnding = nolint ? " " : "\n";
      var tabSpace = nolint ? "" : "\t";
    }

    assert.eq( ( typeof x ) , "object" , "tojsonObject needs object, not [" + ( typeof x ) + "]" );

    if (!indent)
        indent = "";

    if ( x.hasOwnProperty("__str__")) {
        return x.__str__();
    }

    if ( typeof( x.tojson ) == "function" && x.tojson != tojson ) {
        return x.tojson(indent,nolint,html);
    }

    if ( typeof( x.constructor.tojson ) == "function" && x.constructor.tojson != tojson ) {
        return x.constructor.tojson( x, indent , nolint, html );
    }

    if ( x.toString() == "[object MaxKey]" )
        return "{ $maxKey : 1 }";
    if ( x.toString() == "[object MinKey]" )
        return "{ $minKey : 1 }";

    var s = "{" + lineEnding;

    // push one level of indent
    indent += tabSpace;

    var total = 0;
    for ( var k in x ) total++;
    if ( total == 0 ) {
        s += indent + lineEnding;
    }

    var keys = x;
    if ( typeof( x._simpleKeys ) == "function" )
        keys = x._simpleKeys();
    var num = 1;
    for ( var k in keys ){
        var val = x[k];

        s += indent + "\"" + k + "\" : " + tojson( val, indent , nolint );
        if (num != total) {
            s += ",";
            num++;
        }
        s += lineEnding;
    }

    // pop one level of indent
    indent = indent.substring(1);
    return s + indent + "}";
}

shellPrint = function( x ){
    it = x;
    if ( x != undefined )
        shellPrintHelper( x );
}

printjson = function(x){
    print( tojson( x ) );
}

shellPrintHelper = function( x ){

    if ( typeof( x ) == "undefined" ){

        return;
    }
    
    if ( x == null ){
        print( "null" );
        return;
    }

    if ( typeof x != "object" ) 
        return print( x );
    
    var p = x.shellPrint;
    if ( typeof p == "function" )
        return x.shellPrint();

    var p = x.tojson;
    if ( typeof p == "function" )
        print( x.tojson() );
    else
        print( tojson( x ) );
}

shellHelper = function( command , rest , shouldPrint ){
    command = command.trim();
    var args = rest.trim().replace(/;$/,"").split( "\s+" );
    
    if ( ! shellHelper[command] )
        throw "no command [" + command + "]";
    
    var res = shellHelper[command].apply( null , args );
    if ( shouldPrint ){
        shellPrintHelper( res );
    }
    return res;
}

help = shellHelper.help = function(){
    print( "HELP" );
    print( "\t" + "show dbs                     show database names");
    print( "\t" + "show collections             show collections in current database");
    print( "\t" + "show users                   show users in current database");
    print( "\t" + "show profile                 show most recent system.profile entries with time >= 1ms");
    print( "\t" + "use <db name>                set curent database to <db name>" );
    print( "\t" + "db.help()                    help on DB methods");
    print( "\t" + "db.foo.help()                help on collection methods");
    print( "\t" + "db.foo.find()                list objects in collection foo" );
    print( "\t" + "db.foo.find( { a : 1 } )     list objects in foo where a == 1" );
    print( "\t" + "it                           result of the last line evaluated; use to further iterate");
}

if ( typeof( Map ) == "undefined" ){
    Map = function(){
        this._data = {};
    }
}

Map.hash = function( val ){
    if ( ! val )
        return val;

    switch ( typeof( val ) ){
    case 'string':
    case 'number':
    case 'date':
        return val.toString();
    case 'object':
    case 'array':
        var s = "";
        for ( var k in val ){
            s += k + val[k];
        }
        return s;
    }

    throw "can't hash : " + typeof( val );
}

Map.prototype.put = function( key , value ){
    var o = this._get( key );
    var old = o.value;
    o.value = value;
    return old;
}

Map.prototype.get = function( key ){
    return this._get( key ).value;
}

Map.prototype._get = function( key ){
    var h = Map.hash( key );
    var a = this._data[h];
    if ( ! a ){
        a = [];
        this._data[h] = a;
    }
    
    for ( var i=0; i<a.length; i++ ){
        if ( friendlyEqual( key , a[i].key ) ){
            return a[i];
        }
    }
    var o = { key : key , value : null };
    a.push( o );
    return o;
}

Map.prototype.values = function(){
    var all = [];
    for ( var k in this._data ){
        this._data[k].forEach( function(z){ all.push( z.value ); } );
    }
    return all;
}

if ( typeof( gc ) == "undefined" ){
    gc = function(){
    }
}
   

Math.sigFig = function( x , N ){
    if ( ! N ){
        N = 3;
    }
    var p = Math.pow( 10, N - Math.ceil( Math.log( Math.abs(x) ) / Math.log( 10 )) );
    return Math.round(x*p)/p;
}

