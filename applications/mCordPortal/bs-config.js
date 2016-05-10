
/*
 |--------------------------------------------------------------------------
 | Browser-sync config file
 |--------------------------------------------------------------------------
 |
 | For up-to-date information about the options:
 |   http://www.browsersync.io/docs/options/
 |
 | There are more options than you see here, these are just the ones that are
 | set internally. See the website for more info.
 |
 |
 */

var httpProxy = require('http-proxy');
var environment = process.env.NODE_ENV;

if (environment){
  var conf = require(`./env/${environment}.js`);
}
else{
  var conf = require('./env/default.js')
}

var proxy = httpProxy.createProxyServer({
  target: conf.host || 'http://0.0.0.0:9999'
});

proxy.on('error', function(error, req, res) {
  console.log('------------------------------------------------------');
  // res.writeHead(500, {
  //   'Content-Type': 'text/plain'
  // });
  console.error('[Proxy]', error);
  console.log('------------------------------------------------------');
});

module.exports = {
  "files": [
    './src/**/*.css',
    './src/**/*.js',
    './src/**/*.json',
    './src/**/*.html',
    './src/**/*.jpg',
    './src/**/*.png',
    './src/**/*.gif'
  ],
  "server": {
    baseDir: './src',
    //directory: true,
    routes: {
      '/rs/dashboard': './mocks/dashboard.json',
      '/rs/bundle': './mocks/bundle.json',
      '/rs/users': './mocks/users.json'
    },
    middleware: function(req, res, next){
      if(
        req.url.indexOf('/xos/') !== -1 ||
        req.url.indexOf('/xoslib/') !== -1 ||
        req.url.indexOf('/hpcapi/') !== -1
      ){
        if(req.headers['X-CSRFToken']){
          req.headers['x-csrftoken'] = req.headers['x-csrftoken'];
          req.headers.cookie = `xoscsrftoken=${req.headers['x-csrftoken']}; xossessionid=${req.headers['sessionid']}`;
        }
        console.log(`proxied: ${req.url}`, req.headers['x-csrftoken'], req.headers.cookie);
        proxy.web(req, res);
      }
      else{
        next();
      }
    }
  },
  "port": 3000,
  "open": "local"
};