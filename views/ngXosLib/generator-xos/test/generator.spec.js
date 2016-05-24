'use strict';

const path = require('path');
const helpers = require('yeoman-test');
const assert = require('yeoman-assert');
const rimraf = require('rimraf');
const mockery = require('mockery');
const wiredep = require('wiredep');

const firstCharTouppercase = string => string.replace(/^./, string[0].toUpperCase())

// get bower deps installed in ngXosLib
let bowerDeps = wiredep({
  cwd: path.join(__dirname, '../../'), // pretending to be in the ngXosLib root
  exclude: ['Chart.js']
});
bowerDeps = bowerDeps.js.map(d => {
  let path = d.match(/bower_components\/([1-9a-zA-Z\-`.]+)\//);
  if(path){
    return path[1];
  }
});

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
}

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
    assert.fileContent(`${testPath}gulp/build.js`, `options.static + 'js/vendor/xos${fileName}Vendor.js'`)
    assert.fileContent(`${testPath}gulp/build.js`, `options.static + 'js/xos${fileName}.js'`)
    assert.fileContent(`${testPath}gulp/build.js`, `options.static + 'css/xos${fileName}.css'`)
    assert.fileContent(`${testPath}gulp/build.js`, `.pipe(concat('xos${fileName}Vendor.js'))`)
  });

  after(done => {
    // deleting the folder used for test
    rimraf(testPath, {}, done)
  });
});