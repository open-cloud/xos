var gulp = require('gulp');
var uglify = require('gulp-uglify');
var concat = require("gulp-concat");
var ngAnnotate = require('gulp-ng-annotate');
var angularFilesort = require('gulp-angular-filesort');

module.exports = function(options){
  gulp.task('helpers', function(){
    return gulp.src([options.xosHelperSource + '**/*.js'])
      .pipe(angularFilesort())
      .pipe(concat('ngXosHelpers.js'))
      .pipe(ngAnnotate())
      .pipe(uglify())
      .pipe(gulp.dest(options.ngXosVendor));
  });
};