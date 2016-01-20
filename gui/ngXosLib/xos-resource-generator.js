'use strict';

var fs = require('fs');
var CodeGen = require('swagger-js-codegen').CodeGen;
var fetchSchema = require('fetch-swagger-schema');
var P = require('bluebird');
var chalk = require('chalk');
var concat = require('concat')

/////////////
// HELPERS //
/////////////

var fetchSwagger = P.promisify(function(url, done){
  fetchSchema(url, function(error, schema){
    if(error) {
      return done(error);
    }
    done(null, schema);
  });
});

// Write to file promisified
var writeToFile = P.promisify(function(file, content, done) {
  fs.writeFile(file, content, function(err) {
    if(err) {
        return done(err);
    }

    done(null, file + ' has been saved');
  }); 
});

var concatFiles = P.promisify(function(files, dest, done){
  concat(files, dest, function (error) {
    if(error){
      return done(error);
    }
    done();
  })
});

////////////////////
// generator loop //
////////////////////

P.coroutine(function*(){
  
  var generatedFiles = [];

  console.log(chalk.green('Generating APIs '));

  let mainDef = yield fetchSwagger('http://localhost:9999/docs/api-docs/');

  for(let i = 0; i < mainDef.apis.length; i++){
    
    const path = mainDef.apis[i].path.replace('/', '');
  
    process.stdout.write(chalk.green(`Starting ${path} generation `));
    
    let loader = setInterval(function(){
      process.stdout.write(chalk.green('.'));
    }, 500);


    let def = yield fetchSwagger(`http://localhost:9999/docs/api-docs/${path}`);
    yield writeToFile(`api/ng-${path}.js`, CodeGen.getAngularCode({ 
      moduleName: `xos.${path}`, 
      className: `${path}`, 
      swagger: def,
      lint: false,
      template: {
        class: fs.readFileSync('apiTemplates/custom-angular-class.mustache', 'utf-8'),
        method: fs.readFileSync('node_modules/swagger-js-codegen/templates/method.mustache', 'utf-8'),
        request: fs.readFileSync('node_modules/swagger-js-codegen/templates/angular-request.mustache', 'utf-8')
    }
    }));
  
    generatedFiles.push(`api/ng-${path}.js`);

    clearInterval(loader);
    process.stdout.write('\n');
  }

  // TODO rewrite concat to minify API
  // evaluate to use gulp instead to manage this
  // at least minify
  yield concatFiles(generatedFiles, '../static/js/xosApi.js');

  console.log(chalk.green('APIs Ready!'));

  process.exit();

})()
.catch(function(e){
  process.stdout.write('\n');
  console.error(e);
  process.exit(e.code);
});
