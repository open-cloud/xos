
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
    res.writeHead(500, {
        'Content-Type': 'text/plain'
    });
    console.error('[Proxy]', error);
});

module.exports = {
    "files": [
        './src/**/*'
    ],
    "server": {
        baseDir: './src',
        middleware: function(req, res, next){
            if(
              req.url.indexOf('/xos/') !== -1 ||
              req.url.indexOf('/xoslib/') !== -1 ||
              req.url.indexOf('/hpcapi/') !== -1 ||
              req.url.indexOf('/rs/') !== -1
            ){
                if(conf.xoscsrftoken && conf.xossessionid){
                    req.headers.cookie = `xoscsrftoken=${conf.xoscsrftoken}; xossessionid=${conf.xossessionid}`;
                    req.headers['x-csrftoken'] = conf.xoscsrftoken;
                }
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