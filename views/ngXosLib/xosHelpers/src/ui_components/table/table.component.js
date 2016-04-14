/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 3/24/16.
 */

(function () {
  'use strict';


  angular.module('xos.uiComponents.table', [])
    .directive('xosTable', function(){
      return {
        restrict: 'E',
        scope: {
          data: '=',
          config: '='
        },
        template: `
          <!-- <pre>{{vm.data | json}}</pre> -->
          <table ng-class="vm.classes" ng-show="vm.data.length > 0">
            <thead>
              <tr>
                <th ng-repeat="col in vm.columns">{{col.label}}</th>
              </tr>
            </thead>
            <tbody>
              <tr ng-repeat="item in vm.data">
                <td ng-repeat="col in vm.columns">{{item[col.prop]}}</td>
              </tr>
            </tbody>
          </table>
        `,
        bindToController: true,
        controllerAs: 'vm',
        controller: function(){

          if(!this.config){
            throw new Error('[xosTable] Please provide a configuration via the "config" attribute');
          }

          if(!this.config.columns){
            throw new Error('[xosTable] Please provide a columns list in the configuration');
          }

          this.columns = this.config.columns;
          this.classes = this.config.classes || 'table table-striped table-bordered';

          console.log('Bella dello zio, RELOAD');
        }
      }
    })
})();
