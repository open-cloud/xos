// This was generating the files needed from https://github.com/signalfx/swagger-angular-client
// But this module is not parsing the format in which our Swagger is generating JSON files

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

  yield writeToFile(`api/ngXosApi-runtime.js`, `window.XosApi = ${JSON.stringify(mainDef)}`)

  for(let i = 0; i < mainDef.apis.length; i++){
    
    const path = mainDef.apis[i].path.replace('/', '');
  
    process.stdout.write(chalk.green(`Starting ${path} generation `));
    
    let loader = setInterval(function(){
      process.stdout.write(chalk.green('.'));
    }, 500);


    let def = yield fetchSwagger(`http://localhost:9999/docs/api-docs/${path}`);
    
    yield writeToFile(`api/ng-${path}.json`, JSON.stringify(def));
    yield writeToFile(`api/ng-${path}.js`, `window.${path}Api = ${JSON.stringify(def)}`)
  
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
