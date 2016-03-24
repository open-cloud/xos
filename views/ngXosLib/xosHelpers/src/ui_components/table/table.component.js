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
          columns: '='
        },
        template: `
          <!--<pre>{{vm.data | json}}</pre>-->
          <table class="table table-striped" ng-show="vm.data.length > 0">
            <thead>
              <tr>
                <th ng-repeat="col in vm.columns">{{col}}</th>
              </tr>
            </thead>
            <tbody>
              <tr ng-repeat="item in vm.data">
                <td ng-repeat="col in vm.columns">{{item[col]}}</td>
              </tr>
            </tbody>
          </table>
        `,
        bindToController: true,
        controllerAs: 'vm',
        controller: function(){
          console.log(this.data, this.columns);
        }
      }
    })
})();
