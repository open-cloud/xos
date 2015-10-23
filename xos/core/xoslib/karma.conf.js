// Karma configuration
// Generated on Tue Oct 06 2015 09:27:10 GMT+0000 (UTC)

/* eslint indent: [2,2], quotes: [2, "single"]*/

/*eslint-disable*/
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
      'spec/**/*.test.js',

      'spec/**/*.html'
    ],


    // list of files to exclude
    exclude: [
      // '**/xos-utils.test.js', //skip this test, useful in dev, comment before commit
      // '**/xos-backbone.test.js'
    ],


    // preprocess matching files before serving them to the browser
    // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
    preprocessors: {
      'spec/**/*.test.js': ['babel']
    },


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
    browsers: ['PhantomJS'],


    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: false
  });
};
