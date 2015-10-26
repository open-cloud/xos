var express = require('express');  
var request = require('request');
var cors = require('cors');

var apiServerHost = 'http://0.0.0.0:9000';

var app = express();  

app.use(cors());

app.use('/', function(req, res) {  
  var url = apiServerHost + req.url;

  req.headers['X-CSRFToken'] = req.headers['x-csrftoken'];

  var nr = request({url: url, headers: req.headers}, function(err, pres, body){
    if(err){
      console.log(err);
      return res.send(err)
    }
    res.status(pres.statusCode).send(JSON.parse(pres.body));
  });
});

app.listen(process.env.PORT || 4000); 