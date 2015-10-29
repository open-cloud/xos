'use strict';

var gulp = require('gulp');
var wrench = require('wrench');

var options = {};

wrench.readdirSyncRecursive('./gulp')
.map(function(file) {
  console.log(file);
  require('./gulp/' + file)(options);
});

gulp.task('default', ['clean'], function () {
  gulp.start('build');
});
