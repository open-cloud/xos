var express = require('express');  
var request = require('request');

var apiServerHost = 'http://0.0.0.0:9000';

var app = express();  

app.use(function(req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});

app.use('/', function(req, res) {  
  var url = apiServerHost + req.url;

  var nr = request(url, function(err, pres, body){
    if(err){
      console.log(err);
      return res.send(err)
    }
    res.send(pres);
  });
});

app.listen(process.env.PORT || 4000); 