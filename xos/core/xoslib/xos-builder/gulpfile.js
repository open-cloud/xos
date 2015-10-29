'use strict';

var gulp = require('gulp');
var wrench = require('wrench');

var options = {
  scripts: 'src/js/',
  dist: 'dist/'
};

wrench.readdirSyncRecursive('./gulp')
.map(function(file) {
  console.log(file);
  require('./gulp/' + file)(options);
});

gulp.task('default', ['clean'], function () {
  gulp.start('build');
});
