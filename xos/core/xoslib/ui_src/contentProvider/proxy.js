var http = require('http-proxy');

http.createServer(function(req, res) {
  proxy.web(req, res, { target: 'http://localhost:9000' }).listen(3000);
});