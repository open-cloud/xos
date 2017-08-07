
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


// Karma configuration
// Generated on Tue Oct 06 2015 09:27:10 GMT+0000 (UTC)

/* eslint indent: [2,2], quotes: [2, "single"]*/

/*eslint-disable*/
var wiredep = require('wiredep');
var path = require('path');

module.exports = function(config) {
/*eslint-enable*/
  config.set({

    // base path that will be used to resolve all patterns (eg. files, exclude)
    basePath: '',


    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: ['jasmine'],


    // list of files / patterns to load in the browser
    files: [
      'static/js/vendor/jquery-1.11.3.js',
      'static/js/vendor/underscore-min.js',
      'static/js/vendor/backbone.js',
      'static/js/vendor/backbone.wreqr.js',
      'static/js/vendor/backbone.babysitter.js',
      'static/js/vendor/backbone.marionette.js',
      'static/js/vendor/backbone.syphon.js',
      'static/js/xoslib/*.js',

      'spec/helpers/jasmine-jquery.js',
      'spec/**/*.mock.js',
      'spec/**/*.test.js',

      'spec/**/*.html',

      //ng stuff
      // 'static/js/xosContentProvider.js'
    ],


    // list of files to exclude
    exclude: [
      // '**/xos-utils.test.js', //skip this test, useful in dev, comment before commit
      // '**/xos-backbone.test.js',
      // '**/xoslib/**/*.js'
    ],


    // preprocess matching files before serving them to the browser
    // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
    preprocessors: {
      'spec/**/*.test.js': ['babel'],
      'static/js/xoslib/*.js': ['coverage'],
      'static/js/*.js': ['coverage']
    },

    ngHtml2JsPreprocessor: {
      prependPrefix: '../../', //strip the src path from template url (http://stackoverflow.com/questions/22869668/karma-unexpected-request-when-testing-angular-directive-even-with-ng-html2js)
      moduleName: 'templates' // define the template module name
    },

    coverageReporter: {
      type: 'html',
      dir: 'coverage/'
    },

    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['mocha', 'coverage'],


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
    browsers: ['PhantomJS'],


    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: false
  });
};
