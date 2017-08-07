
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

const path = require('path');
const helpers = require('yeoman-test');
const assert = require('yeoman-assert');
const rimraf = require('rimraf');
const mockery = require('mockery');

const firstCharTouppercase = string => string.replace(/^./, string[0].toUpperCase())

const ngVersion = '1.5.8';
const ngXosLibVersion = `1.1.0`;

const bowerDeps = [
  `"angular": "${ngVersion}"`,
  'angular-ui-router',
  `"angular-resource": "${ngVersion}"`,
  `"angular-cookies": "${ngVersion}"`,
  `"angular-animate": "${ngVersion}"`,
  'lodash',
  'angular-chart.js',
  'd3',
  'angular-recursion', // NOTE check if it is still needed
  `"ng-xos-lib": "opencord/ng-xos-lib#${ngXosLibVersion}"`
];

// test values
const viewName = 'testDashboard';
const fileName = firstCharTouppercase(viewName);
const testPath = path.join(__dirname, `../../../ngXosViews/${viewName}/`);

const getDefaultFiles = () => {
  return [
    '.bowerrc',
    '.eslintrc',
    '.gitignore',
    'bower.json',
    'gulpfile.js',
    'karma.conf.js',
    'package.json',
    'src/index.html',
  ].map(i => `${testPath}${i}`);
};

const yeomanUserMock = {
  git: {
    name: () => 'Test User',
    email: () => 'test@mail.org'
  }
};

mockery.enable({
  warnOnReplace: false,
  warnOnUnregistered: false,
  useCleanCache: true,
});
mockery.resetCache();
mockery.registerMock('../node_modules/yeoman-generator/lib/actions/user', yeomanUserMock);

describe('Yeoman XOS generator', function () {

  beforeEach(() => {
  });

  before(done => {
    this.generator = helpers
      .run(require.resolve('../app'))
      .inDir(testPath)
      .withOptions({ 'skip-install': true })
      .withPrompts({
        name: viewName
      })
      .on('end', done);
  });


  it('should generate base files in the correct directory', () => {
    assert.file(getDefaultFiles());
  });

  it('should write username in package & bower json', () => {
    assert.fileContent(`${testPath}package.json`, '"author": "Test User"');
    assert.fileContent(`${testPath}bower.json`, '"Test User <test@mail.org>"')
  });

  it('should add all xosLib dependencies in the dev section of bower.json', () => {
    bowerDeps.forEach(d => {
      assert.fileContent(`${testPath}bower.json`, d);
    });
  });

  it('should set the right module name in all the files', () => {
    assert.fileContent(`${testPath}src/index.html`, `ng-app="xos.${viewName}"`)
    assert.fileContent(`${testPath}src/index.html`, `id="xos${fileName}"`)
    assert.fileContent(`${testPath}src/js/main.js`, `angular.module('xos.${viewName}', [`)
    assert.fileContent(`${testPath}src/sass/main.scss`, `#xos${fileName}`)
  });

  it('should set correct paths in build file', () => {
    assert.fileContent(`${testPath}gulp/build.js`, `angular.module('xos.${viewName}')`)
    assert.fileContent(`${testPath}gulp/build.js`, `options.dashboards + 'xos${fileName}.html'`)
    assert.fileContent(`${testPath}gulp/build.js`, `options.static + 'css/xos${fileName}.css'`)
    assert.fileContent(`${testPath}gulp/build.js`, `.pipe(concat('xos${fileName}.css'))`)
    assert.fileContent(`${testPath}gulp/build.js`, `.pipe(concat('xos${fileName}.js'))`)
    assert.fileContent(`${testPath}gulp/build.js`, `module: 'xos.${viewName}'`)
    assert.fileContent(`${testPath}gulp/build.js`, `options.static + 'vendor/xos${fileName}Vendor.js'`)
    assert.fileContent(`${testPath}gulp/build.js`, `options.static + 'js/xos${fileName}.js'`)
    assert.fileContent(`${testPath}gulp/build.js`, `options.static + 'css/xos${fileName}.css'`)
    assert.fileContent(`${testPath}gulp/build.js`, `.pipe(concat('xos${fileName}Vendor.js'))`)
  });

  after(done => {
    // deleting the folder used for test
    rimraf(testPath, {}, done)
  });
});