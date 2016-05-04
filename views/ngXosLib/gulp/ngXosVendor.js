var gulp = require('gulp');
var uglify = require('gulp-uglify');
var concat = require('gulp-concat');
var wiredep = require('wiredep');

module.exports = function(options){
  gulp.task('vendor', function(){
    var bowerDeps = wiredep().js;
    return gulp.src(bowerDeps)
      .pipe(concat('ngXosVendor.js'))
      .pipe(uglify())
      .pipe(gulp.dest(options.ngXosVendor));
  });
};