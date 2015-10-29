'use strict';

var gulp = require('gulp');
var browserSync = require('browser-sync').create();
var inject = require('gulp-inject');
var runSequence = require('run-sequence');
var angularFilesort = require('gulp-angular-filesort');
var babel = require('gulp-babel');

module.exports = function(options){
  gulp.task('browser', function() {
    browserSync.init({
      server: {
          baseDir: options.src
      }
    });
  });

  gulp.task('babel', function(){
    return gulp.src(options.scripts + '**/*.js')
      .pipe(babel({sourceMaps: true}))
      .pipe(gulp.dest(options.tmp));
  });

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
      .pipe(gulp.dest('./src'));
  });

  gulp.task('serve', function() {
    runSequence(
      'inject',
      'browser'
    );
  });
}