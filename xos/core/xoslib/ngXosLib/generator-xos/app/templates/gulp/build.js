'use strict';

// BUILD
//
// The only purpose of this gulpfile is to build a XOS view and copy the correct files into
// .html => dashboards
// .js (minified and concat) => static/js
//
// The template are parsed and added to js with angular $templateCache

var gulp = require('gulp');
var ngAnnotate = require('gulp-ng-annotate');
var uglify = require('gulp-uglify');
var templateCache = require('gulp-angular-templatecache');
var runSequence = require('run-sequence');
var concat = require('gulp-concat');
var del = require('del');
var wiredep = require('wiredep');
var angularFilesort = require('gulp-angular-filesort');
var _ = require('lodash');
var eslint = require('gulp-eslint');

module.exports = function(options){
  
  // empty the dist folder
  gulp.task('clean', function(){
    return del([options.dist + '**/*']);
  });

  // compile and minify scripts
  gulp.task('scripts', function() {
    return gulp.src([
      options.tmp + '**/*.js'
    ])
    .pipe(ngAnnotate())
    .pipe(angularFilesort())
    .pipe(concat('xos<%= fileName %>.js'))
    .pipe(uglify())
    .pipe(gulp.dest(options.static + 'js/'));
  });

  // set templates in cache
  gulp.task('templates', function(){
    return gulp.src('./src/templates/*.html')
      .pipe(templateCache({
        module: 'xos.<%= name %>',
        root: 'templates/'
      }))
      .pipe(gulp.dest(options.tmp));
  });

  // copy html index to Django Folder
  gulp.task('copyHtml', function(){
    return gulp.src(options.src + 'xos<%= fileName %>.html')
      .pipe(gulp.dest(options.dashboards));
  });

  // minify vendor js files
  gulp.task('wiredep', function(){
    var bowerDeps = wiredep().js;
    if(!bowerDeps){
      return;
    }

    // remove angular (it's already loaded)
    _.remove(bowerDeps, function(dep){
      return dep.indexOf('angular/angular.js') !== -1;
    });

    return gulp.src(bowerDeps)
      .pipe(concat('xos<%= fileName %>Vendor.js'))
      .pipe(uglify())
      .pipe(gulp.dest(options.static + 'js/vendor/'));
  });

  gulp.task('lint', function () {
    return gulp.src(['src/js/**/*.js'])
      .pipe(eslint())
      .pipe(eslint.format())
      .pipe(eslint.failAfterError());
  });

  gulp.task('build', function() {
    runSequence(
      'clean',
      'templates',
      'babel',
      'scripts',
      'wiredep',
      'copyHtml',
      'cleanTmp'
    );
  });
};