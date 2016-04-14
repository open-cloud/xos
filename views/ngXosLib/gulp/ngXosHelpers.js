var gulp = require('gulp');
var uglify = require('gulp-uglify');
var concat = require('gulp-concat');
var ngAnnotate = require('gulp-ng-annotate');
var angularFilesort = require('gulp-angular-filesort');
var gulpDocs = require('gulp-ngdocs');
var del = require('del');
var babel = require('gulp-babel');
const sourcemaps = require('gulp-sourcemaps');

module.exports = function(options){

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
  gulp.task('helpers', ['babel'], function(){
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
    console.log(options);
    return del([options.docs + '**/*']);
  });

  gulp.task('docs', ['cleanDocs'], function(){
    var ngOptions = {
      scripts: [
        'http://ajax.googleapis.com/ajax/libs/angularjs/1.4.7/angular.min.js',
        'http://ajax.googleapis.com/ajax/libs/angularjs/1.4.7/angular-animate.min.js'
      ],
      html5Mode: true,
      title: 'XOS Helpers documentation',
      startPage: '/module',
    }

    return gulpDocs.sections({
      module: {
        glob: [
          options.xosHelperSource + '*.js',
          options.xosHelperSource + 'services/*.js'
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

  gulp.task('dev', function(){
    gulp.watch(options.xosHelperSource + '**/*.js', ['helpersDev']);
  });
};