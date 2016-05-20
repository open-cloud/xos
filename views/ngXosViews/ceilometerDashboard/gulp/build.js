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
var postcss = require('gulp-postcss');
var autoprefixer = require('autoprefixer');
var mqpacker = require('css-mqpacker');
var csswring = require('csswring');

var TEMPLATE_FOOTER = `}]);
angular.module('xos.ceilometerDashboard').run(function($location){$location.path('/')});
angular.element(document).ready(function() {angular.bootstrap(angular.element('#xosCeilometerDashboard'), ['xos.ceilometerDashboard']);});`;

module.exports = function(options){
  
  // delete previous builded file
  gulp.task('clean', function(){
    return del(
      [options.dashboards + 'xosCeilometerDashboard.html'],
      {force: true}
    );
  });

  // minify css
  gulp.task('css', function () {
    var processors = [
      autoprefixer({browsers: ['last 1 version']}),
      mqpacker,
      csswring
    ];
    
    gulp.src([
      `${options.css}**/*.css`,
      `!${options.css}dev.css`
    ])
    .pipe(postcss(processors))
    .pipe(gulp.dest(options.tmp + '/css/'));
  });

  gulp.task('copyCss', ['css'], function(){
    return gulp.src([`${options.tmp}/css/*.css`])
    .pipe(concat('xosCeilometerDashboard.css'))
    .pipe(gulp.dest(options.static + 'css/'))
  });

  // compile and minify scripts
  gulp.task('scripts', function() {
    return gulp.src([
      options.tmp + '**/*.js'
    ])
    .pipe(ngAnnotate())
    .pipe(angularFilesort())
    .pipe(concat('xosCeilometerDashboard.js'))
    //.pipe(uglify())
    .pipe(gulp.dest(options.static + 'js/'));
  });

  // set templates in cache
  gulp.task('templates', function(){
    return gulp.src('./src/templates/*.html')
      .pipe(templateCache({
        module: 'xos.ceilometerDashboard',
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
      //rewriting css path
      // .pipe(replace(/(<link.*">)/, ''))
      // injecting minified files
      .pipe(
        inject(
          gulp.src([
            options.static + 'js/vendor/xosCeilometerDashboardVendor.js',
            options.static + 'js/xosCeilometerDashboard.js',
            options.static + 'css/xosCeilometerDashboard.css'
          ]),
          {ignorePath: '/../../../xos/core/xoslib'}
        )
      )
      .pipe(rename('xosCeilometerDashboard.html'))
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
      .pipe(concat('xosCeilometerDashboardVendor.js'))
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
      'lint',
      'templates',
      'babel',
      'scripts',
      'wiredep',
      'copyHtml',
      'copyCss',
      'cleanTmp'
    );
  });
};