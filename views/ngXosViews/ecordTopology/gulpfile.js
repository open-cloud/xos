
/*
 * Copyright 2017-present Open Networking Foundation

 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at

 * http://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


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
  helpers: '../../../xos/core/xoslib/static/js/vendor/',
  static: '../../../xos/core/xoslib/static/', // this is the django static folder
  dashboards: '../../../xos/core/xoslib/dashboards/' // this is the django html folder
};

wrench.readdirSyncRecursive('./gulp')
.map(function(file) {
  require('./gulp/' + file)(options);
});

gulp.task('default', function () {
  gulp.start('build');
});
