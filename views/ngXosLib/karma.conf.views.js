'use strict';

// THIS KARMA CONF WILL ITERATE THE VIEW FOLDER AND PERFORM ALL THE TESTS!!!

// Karma configuration
// Generated on Tue Oct 06 2015 09:27:10 GMT+0000 (UTC)

/* eslint indent: [2,2], quotes: [2, "single"]*/

const babelPreset = require('babel-preset-es2015');
const fs = require('fs');

const viewDir = '../../xos/core/xoslib/static/js/';
let viewFiles = fs.readdirSync(viewDir);

// hack to avoid testing backbone implementation (they need to be removed)
viewFiles = viewFiles.filter(f => f.indexOf('xosAdminSite') === -1).filter(f => f.indexOf('xosCord') === -1);

viewFiles = viewFiles.filter(f => f.indexOf('js') >= 0).filter(f => f.match(/^xos[A-Z][a-z]+/)).map(f => `${viewDir}${f}`);

/*eslint-disable*/

var files = [
  'node_modules/babel-polyfill/dist/polyfill.js',

  // loading jquery (it's used in tests)
  `./bower_components/jasmine-jquery/lib/jasmine-jquery.js`,
  `./bower_components/jquery/dist/jquery.js`,

  // loading helpers and vendors
  `../../xos/core/xoslib/static/js/vendor/ngXosVendor.js`,
  `../../xos/core/xoslib/static/js/vendor/ngXosHelpers.js`,

  // loading ngMock
  `./bower_components/angular-mocks/angular-mocks.js`,

  // loading templates
  `../../xos/core/xoslib/dashboards/xosDiagnostic.html`,

  // loading files
  `../ngXosViews/*/spec/*.test.js`
].concat(viewFiles);

module.exports = function(config) {
/*eslint-enable*/
  config.set({

    // base path that will be used to resolve all patterns (eg. files, exclude)
    basePath: '',


    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: ['jasmine'],


    // list of files / patterns to load in the browser
    files: files,


    // list of files to exclude
    exclude: [
    ],


    // preprocess matching files before serving them to the browser
    // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
    preprocessors: {
      '../ngXosViews/**/spec/*.test.js': ['babel'],
    },

    babelPreprocessor: {
      options: {
        presets: [babelPreset],
        sourceMap: 'inline'
      }
    },

    //ngHtml2JsPreprocessor: {
    //  stripPrefix: 'src/', //strip the src path from template url (http://stackoverflow.com/questions/22869668/karma-unexpected-request-when-testing-angular-directive-even-with-ng-html2js)
    //  moduleName: 'templates' // define the template module name
    //},

    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['mocha'],


    // web server port
    port: 9876,


    // enable / disable colors in the output (reporters and logs)
    colors: true,


    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,


    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,


    // start these browsers
    // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    browsers: [
      'PhantomJS'
    ],


    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: false
  });
};
