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

var TEMPLATE_HEADER = '/*This code is autogenerated from the templates files */ angular.module("<%= module %>"<%= standalone %>).run(["$templateCache", function($templateCache) {';

module.exports = function(options){
    
  gulp.task('clean', function(){
    return del(['dist/**/*']);
  });

  gulp.task('scripts', function() {
    return gulp.src([
        options.scripts + '**/*.js'
      ])
      .pipe(babel())
      .pipe(ngmin())
      .pipe(angularFilesort())
      .pipe(concat('xosContentProvider.js'))
      .pipe(uglify())
      .pipe(gulp.dest('dist'));
  });

  gulp.task('templates', function(){
    return gulp.src("./src/templates/*.html")
      .pipe(templateCache({
        module: 'xos.contentProviderApp',
        root: '../../static/templates/contentProvider/',
        templateHeader: TEMPLATE_HEADER
      }))
      .pipe(gulp.dest(options.scripts));
  });

  gulp.task('copyJs', function(){
    return gulp.src('dist/xosContentProvider.js')
      .pipe(gulp.dest('../static/js/'))
  });

  gulp.task('copyVendor', function(){
    return gulp.src('dist/xosNgVendor.js')
      .pipe(gulp.dest('../static/js/vendor/'));
  });

  gulp.task('wiredep', function(){
    var bowerDeps = wiredep().js;
    return gulp.src(bowerDeps)
      .pipe(concat('xosNgVendor.js'))
      .pipe(uglify())
      .pipe(gulp.dest('dist'));
  });

  gulp.task('build', function() {
    runSequence(
      'clean',
      'templates',
      'scripts',
      'copyJs',
      'wiredep',
      'copyVendor'
    );
  });
}