'use strict';

const path = require('path');
const helpers = require('yeoman-test');
const assert = require('yeoman-assert');

const testPath = path.join(__dirname, '../../../ngXosViews/test-name/');

const getDefaultFiles = () => {
  return [
    testPath + 'src/index.html',
    testPath + '.bowerrc',
    testPath + '.gitignore',
    testPath + '.eslintrc',
    testPath + 'gulpfile.js',
    testPath + 'package.json',
    testPath + 'bower.json'
  ];
};

describe('Yeoman XOS generator', function () {

  beforeEach(function () {
    this.generator = helpers
      .run(require.resolve('../app'))
      .inDir(testPath)
      .withOptions({ 'skip-install': true })
      .withPrompts({
        name: 'test-name',
        host: 'test-host',
        token: 'test-token',
        session: 'test-session'
      });
  });

  describe('default settings', function () {
    beforeEach(function (done) {
      this.generator.on('end', done);
    });

    it('generate base files', function () {
      assert.file(getDefaultFiles());
    });
  });
});