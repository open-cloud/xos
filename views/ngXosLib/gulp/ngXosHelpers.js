var gulp = require('gulp');
var uglify = require('gulp-uglify');
var concat = require('gulp-concat');
var ngAnnotate = require('gulp-ng-annotate');
var angularFilesort = require('gulp-angular-filesort');
var gulpDocs = require('gulp-ngdocs');

module.exports = function(options){
  gulp.task('helpers', function(){
    return gulp.src([options.xosHelperSource + '**/*.js'])
      .pipe(angularFilesort())
      .pipe(concat('ngXosHelpers.js'))
      .pipe(ngAnnotate())
      .pipe(uglify())
      .pipe(gulp.dest(options.ngXosVendor));
  });

  gulp.task('docs', function(){
    return gulp.src(options.xosHelperSource + '**/*.js')
      .pipe(gulpDocs.process({
        title: 'XOS Helpers Module',
        scripts: [
          'http://ajax.googleapis.com/ajax/libs/angularjs/1.4.7/angular.min.js',
          'http://ajax.googleapis.com/ajax/libs/angularjs/1.4.7/angular-animate.min.js'
        ]
      }))
      .pipe(gulp.dest('./docs'));
  });
};