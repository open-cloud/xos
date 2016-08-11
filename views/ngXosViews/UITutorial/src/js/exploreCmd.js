(function () {
  'use strict';
  angular.module('xos.UITutorial')
  .service('ExploreCmd', function($injector, ResponseHandler, ErrorHandler){

    this.setup = (shell) => {
      shell.setCommandHandler('resource', {
        exec: (cmd, args, done) => {
          switch(args[0]){
            case 'list':
              return listAvailableResources(done);
              break;
            default:
              // use the resource
              const resourceName = args.shift();
              const method = args.shift();
              return consumeResource(resourceName, method, args, done);
          }
        },
        completion: function(cmd, arg, line, callback) {
          const args = ['list'].concat(getAvailableResources());
          if(line.text.match(/resource\s[A-Z][a-z]+\s/)){
            // if arg is a resource, then return available methods
            if(args.indexOf(arg) !== -1){
              arg = '';
            }
            const methods = ['query', 'get', 'save', '$save', 'delete'];
            return callback(shell.bestMatch(arg, methods));
          }
          return callback(shell.bestMatch(arg, args));
        }
      });
    };

    const getAvailableResources = () => {
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

    const listAvailableResources = (done) => {
      const resources = getAvailableResources()
          .reduce((html, i) => `${html}${i}<br/>`, '');
      done(resources);
    }

    const consumeResource = (resourceName, method, args, done) => {

      // TODO if not resourceName/method print cmd instructions

      if(getAvailableResources().indexOf(resourceName) === -1){
        return ErrorHandler.print(`Resource "${resourceName}" does not exists`, done);
      }

      if(['query', 'get', 'save', '$save', 'delete'].indexOf(method) === -1){
        return ErrorHandler.print(`Method "${method}" not allowed`, done);
      }

      let Resource;
      try{
        Resource = $injector.get(resourceName);

        // TODO @Teo if get/delete check for arguments
        let params = {};

        // if the method require arguments checks for them
        if(['get', '$save', 'delete'].indexOf(method) !== -1){
          if(args.length === 0){
            return ErrorHandler.print(`Method "${method}" require parameters`, done);
          }
        }

        // if there are arguments parse them
        if(args.length > 0){
          params = eval(`(${args[0]})`);
        }

        // if it is a query is not possible to use id as parameter
        if(method === 'query' && angular.isDefined(params.id)){
          return ErrorHandler.print(`Is not possible to use "id" as filter in method "${method}", use "get" instead!`, done);
        }

        Resource[method](params).$promise
        .then(res => {
          return ResponseHandler.parse(res, done);
        });
      }
      catch(e){
        return ErrorHandler.print(`Failed to inject resource "${resourceName}"`, done);
      }
    };

  });
})();