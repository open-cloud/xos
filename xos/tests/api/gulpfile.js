var gulp = require('gulp');
var concat = require('gulp-concat');



gulp.task('default', function() {
  gulp.watch('./source/**/*.md', ['concat']);
});

gulp.task('concat', function() {
  return gulp.src([
      './source/base.md',
      './source/utility/group.md',
      './source/utility/**/*.md',
      './source/tenant/group.md',
      './source/tenant/**/*.md',
      './source/service/group.md',
      './source/service/**/*.md',
      './source/core/group.md',
      './source/core/**/*.md',
    ])
    .pipe(concat('../../../apiary.apib', {newLine: '\n \n \n'}))
    .pipe(gulp.dest('./'));
});
