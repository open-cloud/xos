'use strict';

// BUILD
// 
// The only purpose of this gulpfile is to build a XOS view and copy the correct files into
// .html => dashboards
// .js (minified and concat) => static/js
// 
// The template are parsed and added to js with angular $templateCache

var gulp = require('gulp');
var ngmin = require('gulp-ngmin');
var uglify = require('gulp-uglify');
var templateCache = require('gulp-angular-templatecache');
var runSequence = require('run-sequence');
var minifyHtml = require("gulp-minify-html");
var concat = require("gulp-concat");
var del = require('del');
var wiredep = require('wiredep');
var babel = require('gulp-babel');
var angularFilesort = require('gulp-angular-filesort');

module.exports = function(options){
  
  // empty the dist folder
  gulp.task('clean', function(){
    return del([options.dist + '**/*']);
  });

  // compile and minify scripts
  gulp.task('scripts', function() {
    return gulp.src([
        options.scripts + '**/*.js'
      ])
      .pipe(babel())
      .pipe(ngmin())
      .pipe(angularFilesort())
      .pipe(concat('xos<%= fileName %>.js'))
      .pipe(uglify())
      .pipe(gulp.dest(options.dist));
  });

  // set templates in cache
  gulp.task('templates', function(){
    return gulp.src("./src/templates/*.html")
      .pipe(templateCache({
        module: 'xos.<%= name %>',
        root: 'templates/'
      }))
      .pipe(gulp.dest(options.scripts));
  });

  // copy js output to Django Folder
  gulp.task('copyJs', function(){
    return gulp.src('dist/xos<%= fileName %>.js')
      .pipe(gulp.dest(options.static + 'js/'))
  });

  // copy vendor js output to Django Folder
  gulp.task('copyVendor', function(){
    return gulp.src('dist/xosNgVendor.js')
      .pipe(gulp.dest(options.static + 'js/vendor/'));
  });

  // copy html index to Django Folder
  gulp.task('copyHtml', function(){
    return gulp.src(options.src + 'xos<%= fileName %>.html')
      .pipe(gulp.dest(options.dashboards))
  });

  // minify vendor js files
  gulp.task('wiredep', function(){
    var bowerDeps = wiredep().js;
    return gulp.src(bowerDeps)
      .pipe(concat('xosNgVendor.js'))
      .pipe(uglify())
      .pipe(gulp.dest(options.dist));
  });

  // TODO vendor
  // - define a list of common components (eg: angular, angular-route, ...)
  // - find the difference between local components e common components
  // - minify only the local
  // - unify wiredep, filter and copyVendor task

  gulp.task('build', function() {
    runSequence(
      'clean',
      'templates',
      'scripts',
      'copyJs',
      'copyHtml',
      'wiredep',
      'copyVendor'
    );
  });
}