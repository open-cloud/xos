'use strict';

var fs = require('fs');
var CodeGen = require('swagger-js-codegen').CodeGen;
var fetchSchema = require('fetch-swagger-schema');
var P = require('bluebird');
var chalk = require('chalk');

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

////////////////////
// generator loop //
////////////////////

var apiList = ['hpcapi', 'xos', 'xoslib'];

P.coroutine(function*(){
  
  console.log(chalk.green('Generating APIs '));


  for(let i = 0; i < apiList.length; i++){
    
    process.stdout.write(chalk.green(`Starting ${apiList[i]} generation `));
    
    let loader = setInterval(function(){
      process.stdout.write(chalk.green('.'));
    }, 500);

    let def = yield fetchSwagger(`http://localhost:9999/docs/api-docs/${apiList[i]}`);
    yield writeToFile(`api/ng-${apiList[i]}.js`, CodeGen.getAngularCode({ moduleName: `xos.${apiList[i]}`, className: `${apiList[i]}`, swagger: def, lint: false }));
  
    clearInterval(loader);
    process.stdout.write('\n');
  }


  console.log(chalk.green('APIs Ready!'));

  process.exit();

})()
.catch(function(e){
  process.stdout.write('\n');
  console.error(e);
  process.exit(e.code);
});
