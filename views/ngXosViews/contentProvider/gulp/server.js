'use strict';

var gulp = require('gulp');
var browserSync = require('browser-sync').create();
var inject = require('gulp-inject');
var runSequence = require('run-sequence');
var angularFilesort = require('gulp-angular-filesort');
var babel = require('gulp-babel');
var wiredep = require('wiredep').stream;
var httpProxy = require('http-proxy');
var del = require('del');
var sass = require('gulp-sass');
var fs = require('fs');
var path = require('path');

const environment = process.env.NODE_ENV;

if(!fs.existsSync(path.join(__dirname, `../../../env/${environment || 'default'}.js`))){
  if(!environment){
    throw new Error('You should define a default.js config in /views/env folder.');
  }
  else{
    throw new Error(`Since you are loading a custom environment, you should define a ${environment}.js config in /views/env folder.`);
  }
}

var conf = require(path.join(__dirname, `../../../env/${environment || 'default'}.js`));

var proxy = httpProxy.createProxyServer({
  target: conf.host
});


proxy.on('error', function(error, req, res) {
  res.writeHead(500, {
    'Content-Type': 'text/plain'
  });

  console.error('[Proxy]', error);
});

module.exports = function(options){

  gulp.task('browser', function() {
    browserSync.init({
      startPath: '#/',
      snippetOptions: {
        rule: {
          match: /<!-- browserSync -->/i
        }
      },
      server: {
        baseDir: options.src,
        routes: {
          '/xos/core/xoslib/static/js/vendor': options.helpers,
          '/xos/core/static': options.static + '../../static/'
        },
        middleware: function(req, res, next){
          if(
            req.url.indexOf('/api/') !== -1 ||
            req.url.indexOf('/hpcapi/') !== -1
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
      }
    });

    gulp.watch(options.src + 'js/**/*.js', ['js-watch']);
    gulp.watch(options.src + 'vendor/**/*.js', ['bower'], function(){
      browserSync.reload();
    });
    gulp.watch(options.src + '**/*.html', function(){
      browserSync.reload();
    });
    gulp.watch(options.css + '**/*.css', function(){
      browserSync.reload();
    });
    gulp.watch(`${options.sass}/**/*.scss`, ['sass'], function(){
      browserSync.reload();
    });

    gulp.watch([
      options.helpers + 'ngXosHelpers.js',
      options.static + '../../static/xosNgLib.css'
    ], function(){
      browserSync.reload();
    });
  });

  // compile sass
  gulp.task('sass', function () {
    return gulp.src(`${options.sass}/**/*.scss`)
      .pipe(sass().on('error', sass.logError))
      .pipe(gulp.dest(options.css));
  });

  // transpile js with sourceMaps
  gulp.task('babel', function(){
    return gulp.src(options.scripts + '**/*.js')
      .pipe(babel({sourceMaps: true}))
      .pipe(gulp.dest(options.tmp));
  });

  // inject scripts
  gulp.task('injectScript', ['cleanTmp', 'babel'], function(){
    return gulp.src(options.src + 'index.html')
      .pipe(
        inject(
          gulp.src([
            options.tmp + '**/*.js',
            options.helpers + 'ngXosHelpers.js'
          ])
          .pipe(angularFilesort()),
          {
            ignorePath: [options.src, '/../../ngXosLib']
          }
        )
      )
      .pipe(gulp.dest(options.src));
  });

  // inject CSS
  gulp.task('injectCss', function(){
    return gulp.src(options.src + 'index.html')
      .pipe(
        inject(
          gulp.src([
            options.src + 'css/*.css',
            options.static + '../../static/xosNgLib.css'
          ]),
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
      'sass',
      'bower',
      'injectScript',
      'injectCss',
      ['browser']
    );
  });
};
