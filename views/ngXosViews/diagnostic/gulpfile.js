'use strict';

var gulp = require('gulp');
var wrench = require('wrench');

var options = {
  src: 'src/',
  css: 'src/css/',
  sass: 'src/sass/',
  scripts: 'src/js/',
  tmp: 'src/.tmp',
  dist: 'dist/',
  api: '../../ngXosLib/api/',
  helpers: '../../ngXosLib/xosHelpers/src/',
  static: '../../../xos/core/xoslib/static/', // this is the django static folder from dev environment
  dashboards: '../../../xos/core/xoslib/dashboards/' // this is the django html folder
};

wrench.readdirSyncRecursive('./gulp')
.map(function(file) {
  require('./gulp/' + file)(options);
});

gulp.task('default', function () {
  gulp.start('build');
});
