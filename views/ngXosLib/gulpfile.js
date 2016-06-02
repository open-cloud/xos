'use strict';

var gulp = require('gulp');
var wrench = require('wrench');
var path = require('path');

var options = {
  ngXosVendor: '../../xos/core/xoslib/static/js/vendor/', //save here the minfied vendor file, this is automatically loaded in the django page
  ngXosStyles: '../../xos/core/static/', // TODO move in xoslib
  xosHelperSource: './xosHelpers/src/',
  xosHelperTmp: './xosHelpers/.tmp/',
  docs: './docs'
};

wrench.readdirSyncRecursive(path.join(__dirname, './gulp'))
.map(function(file) {
  require(path.join(__dirname, './gulp/' + file))(options);
});

gulp.task('default', function () {
  gulp.start('vendor');
});
