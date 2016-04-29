'use strict';

var gulp = require('gulp');
var wrench = require('wrench');

var options = {
  ngXosVendor: '../../xos/core/xoslib/static/js/vendor/', //save here the minfied vendor file, this is automatically loaded in the django page
  ngXosStyles: '../../xos/core/static/', // TODO move in xoslib
  xosHelperSource: './xosHelpers/src/',
  xosHelperTmp: './xosHelpers/.tmp/',
  docs: './docs'
};

wrench.readdirSyncRecursive('./gulp')
.map(function(file) {
  require('./gulp/' + file)(options);
});

gulp.task('default', function () {
  gulp.start('vendor');
});
