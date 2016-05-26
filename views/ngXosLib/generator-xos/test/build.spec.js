'use strict';
var path = require('path');
var helpers = require('yeoman-test');
var assert = require('yeoman-assert');
var exec = require('child_process').exec;
var fs = require('fs');
const rimraf = require('rimraf');

const getMillisec = min => min * 60 * 1000;
const deleteFile = file => {
  if(fs.existsSync(file)){
    // console.log(`deleting: ${file}`);
    fs.unlinkSync(file);
  }
}

// config files
const cfg = path.join(__dirname, `../../../env/default.js`);

// source files
const viewName = 'testDashboard';
const fileName = viewName.replace(/^./, viewName[0].toUpperCase());
const sourcePath = path.join(__dirname, `../../../ngXosViews/${viewName}/`);

// dest files
const basePath = '../../../../xos/core/xoslib';
const destHtml = path.join(__dirname, basePath + '/dashboards/xosTestDashboard.html');
const destJs = path.join(__dirname, basePath + '/static/js/xosTestDashboard.js');
const destVendor = path.join(__dirname, basePath + '/static/js/vendor/xosTestDashboardVendor.js');
const destCss = path.join(__dirname, basePath + '/static/css/xosTestDashboard.css');

describe('The XOS Build script', function(){
  const buildCmd = 'gulp build';
  
  this.timeout(getMillisec(5));

  before(done => {
    // if `default.js` config is not present
    // create one (we check to avoid screwing up local envs)
    if(!fs.existsSync(cfg)){
      fs.writeFileSync(cfg, 'module.exports = {}');
    }
    
    console.log('Running generator');
    this.generator = helpers
      .run(require.resolve('../app'))
      .inDir(sourcePath)
      .withOptions({ 'skip-install': false })
      .withPrompts({
        name: viewName,
        host: 'test-host',
        token: 'test-token',
        session: 'test-session'
      })
      .on('end', () => {
        process.stdout.write('Installing Node Modules');
        let npmInstall = setInterval(() => {
          process.stdout.write('.');
        }, 1000);
        exec('npm install', {
          cwd: sourcePath
        }, (err) => {
          clearInterval(npmInstall);
          process.stdout.write('\nInstalling Bower Components');
          let bowerInstall = setInterval(() => {
            process.stdout.write('.');
          }, 1000);
          exec('bower install', {
            cwd: sourcePath
          }, (err) => {
            clearInterval(bowerInstall);
            done(err);
          });
        });
      });
  });

  describe('when no styles or vendors are added', () => {
    
    before((done) => {
      process.stdout.write('\nBuilding App');
      let appBuild = setInterval(() => {
        process.stdout.write('.');
      }, 1000);
      exec(buildCmd, {
        cwd: sourcePath
      }, (err) => {
        console.log(err);
        clearInterval(appBuild);
        done(err);
      });
    });

    it('should have build the app', () => {
      assert.file([destHtml, destJs]);
    });

    it('should include only minified files in the index', () => {
      assert.fileContent(destHtml, `<script src="/static/js/xos${fileName}.js"></script>`);
      assert.noFileContent(destHtml, `<!-- bower:css -->`);
      assert.noFileContent(destHtml, `<!-- bower:js -->`);
    });
  });

  describe('when a third party library is added', () => {
    before((done) => {
    process.stdout.write('\nInstalling 3rd party library');
      let bowerInstall = setInterval(() => {
        process.stdout.write('.');
      }, 1000);
      exec('bower install d3 --save', {
        cwd: sourcePath
      }, (err, out) => {
        clearInterval(bowerInstall);
        process.stdout.write('\nBuilding App');
        let appBuild = setInterval(() => {
          process.stdout.write('.');
        }, 1000);
        exec(buildCmd, {
          cwd: sourcePath
        }, (err) => {
          console.log(err);
          clearInterval(appBuild);
          done(err);
        }); 
      });
    });

    it('should have build the app with a vendor file', () => {
      assert.file([destHtml, destJs, destVendor]);
    });

    it('should include only minified files and minified deps in the index', () => {
      assert.fileContent(destHtml, `<script src="/static/js/xos${fileName}.js"></script>`);
      assert.fileContent(destHtml, `<script src="/static/js/vendor/xos${fileName}Vendor.js"></script>`);
      assert.noFileContent(destHtml, `<!-- bower:css -->`);
      assert.noFileContent(destHtml, `<!-- bower:js -->`);
    });
  });

  describe('when some styles are added', () => {
    before((done) => {
      let styleContent = `
        @import '../../../../style/sass/lib/_variables.scss';

        #xosTestDashboard {
          background: $brand-primary;
        }
      `;

      fs.writeFile(`${sourcePath}src/sass/main.scss`, styleContent, function(err) {
        process.stdout.write('\nBuilding the Application');
        let appBuild = setInterval(() => {
          process.stdout.write('.');
        }, 1000);
        exec('bower uninstall d3 --save', {
          cwd: sourcePath
        }, (err, out) => {
          exec(buildCmd, {
            cwd: sourcePath
          }, (err, out) => {
            clearInterval(appBuild);
            done();
          })
        })
      });
    });

    it('should have build the app with a css file', () => {
      assert.file([destHtml, destJs, destCss]);
    });

    it('should include only minified files and minified deps in the index', () => {
      assert.fileContent(destHtml, `<script src="/static/js/xos${fileName}.js"></script>`);
      assert.fileContent(destHtml, `<link rel="stylesheet" href="/static/css/xos${fileName}.css">`);
      assert.noFileContent(destHtml, `<!-- bower:css -->`);
      assert.noFileContent(destHtml, `<!-- bower:js -->`);

      assert.fileContent(destCss, `background:#337ab7`);
    });
  });

  after(done => {
    // deleting the folder used for test
    deleteFile(destHtml);
    deleteFile(destJs);
    deleteFile(destVendor);
    deleteFile(destCss);
    rimraf(sourcePath, {}, done);
  });
});