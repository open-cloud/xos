var gulp = require('gulp');
var concat = require('gulp-concat');



gulp.task('default', function() {
  gulp.watch('./source/**/*.md', ['concat']);
});

gulp.task('concat', function() {
  return gulp.src([
      './source/base.md',
      './source/**/*.md'
    ])
    .pipe(concat('../../../apiary.apib', {newLine: '\n \n \n'}))
    .pipe(gulp.dest('./'));
});
