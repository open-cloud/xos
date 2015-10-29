'use strict';

var gulp = require('gulp');
var browserSync = require('browser-sync').create();
var inject = require('gulp-inject');
var runSequence = require('run-sequence');
var angularFilesort = require('gulp-angular-filesort');
var babel = require('gulp-babel');
var wiredep = require('wiredep').stream;
var httpProxy = require('http-proxy');

var proxy = httpProxy.createProxyServer({
  target: 'http://0.0.0.0:9000'
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
      reloadDelay: 500,
      server: {
        baseDir: options.src,
        middleware: function(req, res, next){
          console.log(req.url);
          if(req.url.indexOf('no_hyperlinks') !== -1){
            proxy.web(req, res);
          }
          else{
            next();
          }
        }
      }
    });

     gulp.watch(options.scripts + '**/*.js', ['js-watch']);
  });

  // transpile js with sourceMaps
  gulp.task('babel', function(){
    return gulp.src(options.scripts + '**/*.js')
      .pipe(babel({sourceMaps: true}))
      .pipe(gulp.dest(options.tmp));
  });

  // inject scripts
  gulp.task('inject', ['babel'],function(){
    return gulp.src(options.src + 'index.html')
      .pipe(
        inject(
          gulp.src(options.tmp + '**/*.js')
          .pipe(angularFilesort()),
          {
            ignorePath: options.src
          }
        )
      )
      .pipe(gulp.dest(options.src));
  });

  // inject bower dependencies with wiredep
  gulp.task('bower', function () {
    gulp.src(options.src + 'index.html')
    .pipe(wiredep({devDependencies: true}))
    .pipe(gulp.dest(options.src));
  });

  //watch js for changes
  gulp.task('js-watch', ['babel'], browserSync.reload);

  gulp.task('serve', function() {
    runSequence(
      'bower',
      'inject',
      ['browser'
      ]
    );
  });
}