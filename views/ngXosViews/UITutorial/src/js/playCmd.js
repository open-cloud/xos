(function () {
  'use strict';
  angular.module('xos.UITutorial')
  .service('PlayCmd', function($compile, $rootScope, _, ErrorHandler){

    // TODO investigate if we can load directives from an app
    const components = [
      {
        name: 'xosTable',
        template: '<xos-table config="config" data="data"></xos-table>',
        scope: {
          config: {
            columns: [
              {label: 'Name', prop: 'name'},
              {label: 'Age', prop: 'age'}
            ]
          },
          data: [
            {name: 'Jhon', age: 23},
            {name: 'Mike', age: 24}
          ]
        }
      },
      {
        name: 'xosForm',
        template: '<xos-form config="config" ng-model="data"></xos-form>',
        scope: {
          config: {
            fields: {
              name: {
                type: 'text'
              },
              age: {
                type: 'number'
              }
            },
            actions: [
              {
                label: 'Print',
                cb: (model) => {
                  console.log(model);
                }
              }
            ]
          },
          data: {name: 'Jhon', age: 23}
        }
      }
    ];

    this.componentCompletion = (cmd, arg, line, done) => {
      const componentsName = components.map(c => c.name);
      return done(this.shell.bestMatch(arg, componentsName));
    };

    this.componentExec = (cmd, args, done) => {
      const targetComponent = args[0];

      if(!targetComponent){
        return ErrorHandler.print(`Component "${targetComponent}" does not exists`, done);
      }

      this.attachComponent(targetComponent, done);
    };

    this.getComponentsDetails = (componentName, components) => {
      return _.find(components, {name: componentName});
    };

    this.attachComponent = (targetComponent, done) => {
      this.scope = $rootScope.$new();
      targetComponent = this.getComponentsDetails(targetComponent, components);

      angular.extend(this.scope, targetComponent.scope);

      $rootScope.$emit('uiTutorial.attachScope', this.scope);

      const directive = $compile(targetComponent.template)(this.scope);
      const container = $('#directive-container');
      container.html('');
      container.append( directive );
      done('Component added');
    };

    $rootScope.$on('uiTutorial.applyScope', (e, scope) => {
      this.scope.config = scope.config;
      this.scope.data = scope.data;
    });

    this.setup = (shell) => {
      this.shell = shell;
      shell.setCommandHandler('component', {
        exec: this.componentExec,
        completion: this.componentCompletion
      });

      // activate listener to enable/disable shell
      $('.component-container').click((e) => {
        this.shell.deactivate();
      });

      $('#shell-panel').click((e) => {
        this.shell.activate();
      });
    };

    
  });
})();