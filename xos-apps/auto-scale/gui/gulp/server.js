'use strict';

var gulp = require('gulp');
var browserSync = require('browser-sync').create();
var inject = require('gulp-inject');
var runSequence = require('run-sequence');
var angularFilesort = require('gulp-angular-filesort');
var babel = require('gulp-babel');
var wiredep = require('wiredep').stream;
var del = require('del');
var httpProxy = require('http-proxy');

const environment = process.env.NODE_ENV;

if (environment){
  var conf = require(`../env/${environment}.js`);
}
else{
  var conf = require('../env/default.js')
}

console.log(conf);

var proxy = httpProxy.createProxyServer({
  target: conf.host || 'http://0.0.0.0:9999'
});

proxy.on('error', function(error, req, res) {
  res.writeHead(500, {
    'Content-Type': 'text/plain'
  });

  console.error('[Proxy]', error);
});

module.exports = function(options){

  // open in browser with sync and proxy to 0.0.0.0
  gulp.task('browser', function() {
    browserSync.init({
      // reloadDelay: 500,
      // logLevel: 'debug',
      // logConnections: true,
      // directory: true,
      startPath: '#/',
      snippetOptions: {
        rule: {
          match: /<!-- browserSync -->/i
        }
      },
      server: {
        baseDir: options.src,
        middleware: function(req, res, next){
          if(
            req.url.indexOf('autoscaledata') !== -1
          ){
            proxy.web(req, res);
          }
          else{
            next();
          }
        }
      }
    });

    gulp.watch(options.src + 'js/**/*.js', ['js-watch']);
    
    gulp.watch(options.src + 'vendor/**/*.js', ['bower'], function(){
      browserSync.reload();
    });
    gulp.watch(options.src + '**/*.html', function(){
      browserSync.reload();
    });
    gulp.watch(options.src + '**/*.css', function(){
      browserSync.reload();
    });
  });

  // transpile js with sourceMaps
  gulp.task('babel', function(){
    return gulp.src([options.scripts + '**/*.js'])
      .pipe(babel({sourceMaps: true}))
      .pipe(gulp.dest(options.tmp));
  });

  // inject scripts
  gulp.task('injectScript', function(){
    runSequence(
       'cleanTmp',
       'babel',
        function() {
          return gulp.src(options.src + 'index.html')
          .pipe(
            inject(
              gulp.src([
                options.tmp + '**/*.js',
                options.api + '*.js',
                options.helpers + '**/*.js'
              ])
              // .pipe(debug({title: 'unicorn:'}))
              .pipe(angularFilesort()),
              {
                ignorePath: [options.src, '/../../ngXosLib']
              }
            )
          )
          .pipe(gulp.dest(options.src));
        }
      );
  });

  // inject CSS
  gulp.task('injectCss', function(){
    return gulp.src(options.src + 'index.html')
      .pipe(
        inject(
          gulp.src(options.src + 'css/*.css'),
          {
            ignorePath: [options.src]
          }
          )
        )
      .pipe(gulp.dest(options.src));
  });

  // inject bower dependencies with wiredep
  gulp.task('bower', function () {
    return gulp.src(options.src + 'index.html')
    .pipe(wiredep({devDependencies: true}))
    .pipe(gulp.dest(options.src));
  });

  gulp.task('js-watch', ['injectScript'], function(){
    browserSync.reload();
  });

  gulp.task('cleanTmp', function(){
    return del([options.tmp + '**/*']);
  });

  gulp.task('serve', function() {
    runSequence(
      'bower',
      'injectScript',
      'injectCss',
      ['browser']
    );
  });
};
