'use strict';

var gulp = require('gulp');
var wrench = require('wrench');

var options = {
  ngXosVendor: '../static/js/vendor/' //save here the minfied vendor file, this is automatically loaded in the django page
};

wrench.readdirSyncRecursive('./gulp')
.map(function(file) {
  require('./gulp/' + file)(options);
});

gulp.task('default', function () {
  gulp.start('vendor');
});
