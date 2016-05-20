// Karma configuration
// Generated on Tue Oct 06 2015 09:27:10 GMT+0000 (UTC)

/* eslint indent: [2,2], quotes: [2, "single"]*/

// CONFIGURATION FOR JENKINS TESTS

/*eslint-disable*/
var wiredep = require('wiredep');
var path = require('path');

var bowerComponents = wiredep({devDependencies: true})[ 'js' ].map(function( file ){
  return path.relative(process.cwd(), file);
});

var files = bowerComponents.concat([
  'node_modules/babel-polyfill/dist/polyfill.js',
  '../../xos/core/xoslib/static/js/vendor/ngXosHelpers.js',
  'xosHelpers/spec/**/*.test.js'
]);

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
      'xosHelpers/**/*.js': ['babel', 'coverage'],
    },

    babelPreprocessor: {
      options: {
        presets: ['es2015'],
        sourceMap: 'inline'
      },
      filename: function (file) {
        return file.originalPath;
      },
    },

    //ngHtml2JsPreprocessor: {
    //  stripPrefix: 'src/', //strip the src path from template url (http://stackoverflow.com/questions/22869668/karma-unexpected-request-when-testing-angular-directive-even-with-ng-html2js)
    //  moduleName: 'templates' // define the template module name
    //},

    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['dots', 'junit', 'coverage'],

    junitReporter: {
      outputDir: 'test-result',
      useBrowserName: false,
      outputFile: 'test-results.xml'
    },

    coverageReporter: {
      type: 'cobertura',
      subdir: '.',
      dir: 'test-result/'
    },

    // web server port
    port: 9876,


    // enable / disable colors in the output (reporters and logs)
    colors: true,


    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_ERROR,


    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: false,


    // start these browsers
    // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    browsers: ['PhantomJS'],


    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: true
  });
};
