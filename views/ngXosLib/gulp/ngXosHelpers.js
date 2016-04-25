var gulp = require('gulp');
var uglify = require('gulp-uglify');
var concat = require('gulp-concat');
var ngAnnotate = require('gulp-ng-annotate');
var angularFilesort = require('gulp-angular-filesort');
var gulpDocs = require('gulp-ngdocs');
var del = require('del');
var babel = require('gulp-babel');
const sourcemaps = require('gulp-sourcemaps');
var browserSync = require('browser-sync').create();
var rename = require('gulp-rename');
var sass = require('gulp-sass');

module.exports = function(options){

  gulp.task('style', function(){
    return gulp.src(`${options.xosHelperSource}styles/main.scss`)
      .pipe(sourcemaps.init())
      .pipe(sass().on('error', sass.logError))
      .pipe(rename('xosNgLib.css'))
      .pipe(sourcemaps.write())
      .pipe(gulp.dest(options.ngXosStyles));
  });

  // transpile js with sourceMaps
  gulp.task('babel', function(){
    return gulp.src(options.xosHelperSource + '**/*.js')
      .pipe(babel({
        presets: ['es2015']
      }))
      .pipe(gulp.dest(options.xosHelperTmp));
  });

  gulp.task('babelDev', function(){
    return gulp.src(options.xosHelperSource + '**/*.js')
      .pipe(sourcemaps.init())
      .pipe(babel({
        presets: ['es2015']
      }))
      .pipe(sourcemaps.write('./maps'))
      .pipe(gulp.dest(options.xosHelperTmp));
  });

  // build
  gulp.task('helpers', ['babel', 'style'], function(){
    return gulp.src([options.xosHelperTmp + '**/*.js'])
      .pipe(angularFilesort())
      .pipe(concat('ngXosHelpers.js'))
      .pipe(ngAnnotate())
      .pipe(uglify())
      .pipe(gulp.dest(options.ngXosVendor));
  });

  // build Dev (no minify, sourcemaps)
  gulp.task('helpersDev', ['babelDev'], function(){
    return gulp.src([options.xosHelperTmp + '**/*.js'])
      .pipe(angularFilesort())
      .pipe(concat('ngXosHelpers.js'))
      .pipe(ngAnnotate())
      .pipe(gulp.dest(options.ngXosVendor));
  });

  gulp.task('cleanDocs', function(){
    return del([options.docs + '**/*']);
  });

  gulp.task('makeDocs', ['cleanDocs'], function(){
    var ngOptions = {
      scripts: [
        'https://cdnjs.cloudflare.com/ajax/libs/angular.js/1.4.7/angular.js',
        'https://cdnjs.cloudflare.com/ajax/libs/angular.js/1.4.7/angular-animate.js',
        'https://cdnjs.cloudflare.com/ajax/libs/angular.js/1.4.7/angular-cookies.min.js',
        'https://cdnjs.cloudflare.com/ajax/libs/angular.js/1.4.7/angular-resource.js',
        'https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.11.2/lodash.js',
        `./${options.ngXosVendor}ngXosHelpers.js`
      ],
      styles: [
        'https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.6/css/bootstrap.css',
      ],
      html5Mode: false,
      title: 'XOS Helpers documentation',
      startPage: '/module',
    }

    return gulpDocs.sections({
      module: {
        glob: [
          options.xosHelperSource + '*.js',
          options.xosHelperSource + 'services/*.js',
          options.xosHelperSource + 'ui_components/**/*.js'
        ],
        title: 'Module Documentation',
      },
      'rest-api': {
        glob: [
          options.xosHelperSource + 'services/rest/*.js'
        ],
        api: true,
        title: 'API Documentation',
      }
    }).pipe(gulpDocs.process(ngOptions)).pipe(gulp.dest('./docs'));
  });

  gulp.task('serveDocs', function(){
    browserSync.init({
      server: {
        baseDir: './docs',
        routes: {
          '/xos/core/xoslib/static/js/vendor': options.ngXosVendor
        }
      }
    });
  });

  gulp.task('docs', ['makeDocs', 'serveDocs'], function(){
    
    var files = [
      options.xosHelperSource + '*.js',
      options.xosHelperSource + 'services/*.js',
      options.xosHelperSource + 'ui_components/**/*.js'
    ];

    gulp.watch(files, ['makeDocs']);

    gulp.watch(files, function(){
      browserSync.reload();
    });
  })

  gulp.task('dev', function(){
    gulp.watch(`${options.xosHelperSource}**/*.scss`, ['style']);
    gulp.watch(options.xosHelperSource + '**/*.js', ['helpersDev']);
  });
};