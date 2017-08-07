
/*
 * Copyright 2017-present Open Networking Foundation

 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at

 * http://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


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