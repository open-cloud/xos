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
var inject = require('gulp-inject');
var rename = require('gulp-rename');
var replace = require('gulp-replace');

var TEMPLATE_FOOTER = '}]);angular.bootstrap(angular.element(\'#xos<%= fileName %>\'), [\'xos.<%= name %>\']);';
module.exports = function(options){
  
  // delete previous builded file
  gulp.task('clean', function(){
    return del(
      [options.dashboards + 'xos<%= fileName %>.html'],
      {force: true}
    );
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
        root: 'templates/',
        templateFooter: TEMPLATE_FOOTER
      }))
      .pipe(gulp.dest(options.tmp));
  });

  // copy html index to Django Folder
  gulp.task('copyHtml', ['clean'], function(){
    return gulp.src(options.src + 'index.html')
      // remove dev dependencies from html
      .pipe(replace(/<!-- bower:css -->(\n.*)*\n<!-- endbower --><!-- endcss -->/, ''))
      .pipe(replace(/<!-- bower:js -->(\n.*)*\n<!-- endbower --><!-- endjs -->/, ''))
      .pipe(replace(/ng-app=".*"\s/, ''))
      // injecting minified files
      .pipe(
        inject(
          gulp.src([
            options.static + 'js/vendor/xos<%= fileName %>Vendor.js',
            options.static + 'js/xos<%= fileName %>.js'
          ])
        )
      )
      .pipe(rename('xos<%= fileName %>.html'))
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
      'templates',
      'babel',
      'scripts',
      'wiredep',
      'copyHtml',
      'cleanTmp'
    );
  });
};