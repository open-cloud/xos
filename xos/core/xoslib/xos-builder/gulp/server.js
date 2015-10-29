'use strict';

var gulp = require('gulp');
var browserSync = require('browser-sync').create();
var inject = require('gulp-inject');

module.exports = function(options){
  gulp.task('browser', function() {
    browserSync.init({
      server: {
          baseDir: "./src"
      }
    });
  });

  gulp.task('inject', function(){
    return gulp.src('./src/index.html')
      .pipe(inject(gulp.src('./src/js/**/*.js', {read: false})))
      .pipe(gulp.dest('./src'));
  });
}