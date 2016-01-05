'use strict';

var gulp = require('gulp');
var wrench = require('wrench');

var options = {
  src: 'src/',
  css: 'src/css/',
  scripts: 'src/js/',
  tmp: 'src/.tmp',
  dist: 'dist/',
  api: '../../ngXosLib/api/',
  helpers: '../../ngXosLib/xosHelpers/src/',
  static: '../../static/', // this is the django static folder
  dashboards: '../../dashboards/' // this is the django html folder
};

wrench.readdirSyncRecursive('./gulp')
.map(function(file) {
  require('./gulp/' + file)(options);
});

gulp.task('default', function () {
  gulp.start('build');
});
