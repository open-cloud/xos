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

gulp.task('clean', function(){
  return del(['dist/**/*']);
});

gulp.task('scripts', function() {
  return gulp.src([
      'src/xosContentProvider.js',
      'src/templates.js'
    ])
    .pipe(ngmin())
    .pipe(concat('xosContentProvider.js'))
    .pipe(uglify())
    .pipe(gulp.dest('dist'));
});

gulp.task('templates', function(){
  return gulp.src("./src/templates/*.html")
    .pipe(templateCache({
      module: 'xos.contentProviderApp',
      root: '../../static/templates/contentProvider/'
    }))
    .pipe(gulp.dest("src"));
});

gulp.task('copyJs', function(){
  return gulp.src('dist/xosContentProvider.js')
    .pipe(gulp.dest('../static/js/'))
});

gulp.task('default', function() {
  runSequence(
    'clean',
    'templates',
    'scripts',
    'copyJs'
  );
});
