(function () {
  'use strict';
  angular.module('xos.UITutorial')
  .service('ExploreCmd', function($injector, ResponseHandler, ErrorHandler){

    this.resourceExec = (cmd, args, done) => {
      switch(args[0]){
        case 'list':
          return this.listAvailableResources(done);
          break;
        default:
          // use the resource
          const resourceName = args.shift();
          const method = args.shift();
          return this.consumeResource(resourceName, method, args, done);
      }
    };

    this.resourceCompletion = (cmd, arg, line, done) => {
      const args = ['list'].concat(this.getAvailableResources());
      if(line.text.match(/resource\s[A-Z][a-z]+\s/)){
        // if arg is a resource, then return available methods
        if(args.indexOf(arg) !== -1){
          arg = '';
        }
        const methods = ['query', 'get', 'save', '$save', 'delete'];
        return done(this.shell.bestMatch(arg, methods));
      }
      return done(this.shell.bestMatch(arg, args));
    };

    this.setup = (shell) => {
      this.shell = shell;
      shell.setCommandHandler('resource', {
        exec: this.resourceExec,
        completion: this.resourceCompletion
      });
    };

    this.getAvailableResources = () => {
      return angular.module('xos.helpers')._invokeQueue
          .filter((d) => {
            if(d[1] !== 'service'){
              return false;
            }
            const serviceDeps = d[2][1];
            return serviceDeps.indexOf('$resource') !== -1;
          })
          .reduce((list, i) => list.concat([i[2][0]]), []);
    }

    this.listAvailableResources = (done) => {
      // TODO use a template
      const resources = this.getAvailableResources()
          .reduce((html, i) => `${html}${i}<br/>`, '');
      done(resources);
    }

    this.consumeResource = (resourceName, method, args, done) => {

      // TODO if not resourceName/method print cmd instructions

      if(this.getAvailableResources().indexOf(resourceName) === -1){
        return ErrorHandler.print(`Resource "${resourceName}" does not exists`, done);
      }

      if(['query', 'get', 'save', '$save', 'delete'].indexOf(method) === -1){
        return ErrorHandler.print(`Method "${method}" not allowed`, done);
      }

      // TODO @Teo if get/delete check for arguments
      let params = {};

      // if the method require arguments checks for them
      if(['get', '$save', 'delete'].indexOf(method) !== -1){
        if(args.length === 0){
          return ErrorHandler.print(`Method "${method}" require parameters`, done);
        }
      }

      // if there are arguments parse them
      // TODO wrap in a try catch, we have no guarantee that a user insert the correct params
      if(args.length > 0){
        params = eval(`(${args[0]})`);
      }

      // if it is a query is not possible to use id as parameter
      if(method === 'query' && angular.isDefined(params.id)){
        return ErrorHandler.print(`Is not possible to use "id" as filter in method "${method}", use "get" instead!`, done);
      }

      let Resource;
      try{
        Resource = $injector.get(resourceName);
        Resource[method](params).$promise
        .then(res => {
          const jsCode = `${resourceName}.${method}(${Object.keys(params).length > 0 ? JSON.stringify(params): ''})`;
          return ResponseHandler.parse(res, jsCode, done);
        })
        .catch(e => {
          if(e.status === 404){
            return ErrorHandler.print(`${resourceName} with method "${method}" and parameters ${JSON.stringify(params)} ${e.data.detail}`, done);
          }
        });
      }
      catch(e){
        console.error(e);
        return ErrorHandler.print(`Failed to inject resource "${resourceName}"`, done);
      }
    };

  });
})();