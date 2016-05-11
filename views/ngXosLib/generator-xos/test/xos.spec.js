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
bowerDeps = bowerDeps.js.map(d => d.match(/bower_components\/([a-zA-Z\-`.]+)\//)[1]);

// test values
const viewName = 'testDashboard';
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
        name: viewName,
        host: 'test-host',
        token: 'test-token',
        session: 'test-session'
      })
      .on('end', done);
  });


  it('should generate base files in the correct directory', () => {
    assert.file(getDefaultFiles());
  });

  it('should create the env file with correct params', () => {
    assert.fileContent(`${testPath}env/default.js`, 'host: \'test-host\'');
    assert.fileContent(`${testPath}env/default.js`, 'xoscsrftoken: \'test-token\'');
    assert.fileContent(`${testPath}env/default.js`, 'xossessionid: \'test-session\'');
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
    assert.fileContent(`${testPath}src/index.html`, `id="xos${firstCharTouppercase(viewName)}"`)
    assert.fileContent(`${testPath}src/js/main.js`, `angular.module('xos.${viewName}', [`)
    assert.fileContent(`${testPath}src/sass/main.scss`, `#xos${firstCharTouppercase(viewName)}`)
  });

  xit('should create a correct gulp build file', () => {
    
  });

  after(done => {
    // deleting the folder used for test
    rimraf(testPath, {}, done)
  });
});