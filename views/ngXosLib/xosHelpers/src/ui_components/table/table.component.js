/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 3/24/16.
 */

(function () {
  'use strict';

  /**
  * @ngdoc overview
  * @name xos.uiComponents.table
  * @description A table component
  **/

  angular.module('xos.uiComponents.table', [])

    /**
    * @ngdoc directive
    * @name xos.uiComponents.table.directive:xosTable
    * @restrict E
    * @description The xos-table directive
    * @element ANY
    * @scope
    * @example

  <example module="sampleModule1">
    <file name="index.html">
      <div ng-controller="SampleCtrl1 as vm">
        <xos-table data="vm.data" config="vm.config"></xos-table>
        </xos-table>
      </div>
    </file>
    <file name="script.js">
      angular.module('sampleModule1', ['xos.uiComponents.table'])
      .controller('SampleCtrl1', function(){
        this.config = {
          columns: [
            {
              label: 'First Name',
              prop: 'name'
            },
            {
              label: 'Last Name',
              prop: 'lastname'
            }
          ]
        };

        this.data = [
          {
            name: 'John',
            lastname: 'Doe'
          },
          {
            name: 'Gili',
            lastname: 'Fereydoun'
          }
        ]
      });
    </file>
  </example>

    <example module="sampleModule2">
    <file name="index.html">
      <div ng-controller="SampleCtrl2 as vm">
        <xos-table data="vm.data" config="vm.config"></xos-table>
        </xos-table>
      </div>
    </file>
    <file name="script.js">
      angular.module('sampleModule2', ['xos.uiComponents.table'])
      .controller('SampleCtrl2', function(){
        this.config = {
          columns: [
            {
              label: 'First Name',
              prop: 'name'
            },
            {
              label: 'Last Name',
              prop: 'lastname'
            }
          ],
          classes: 'table table-striped table-condensed',
          actions: [
            {
              label: 'delete',
              icon: 'remove',
              cb: (user) => {
                console.log(user);
              },
              color: 'red'
            }
          ]
        };

        this.data = [
          {
            name: 'John',
            lastname: 'Doe'
          },
          {
            name: 'Gili',
            lastname: 'Fereydoun'
          }
        ]
      });
    </file>
  </example>

    **/

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
                <th ng-if="vm.config.actions">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr ng-repeat="item in vm.data">
                <td ng-repeat="col in vm.columns">{{item[col.prop]}}</td>
                <td ng-if="vm.config.actions">
                  <i
                    ng-repeat="action in vm.config.actions"
                    ng-click="action.cb(item)"
                    class="glyphicon glyphicon-{{action.icon}}"
                    style="color: {{action.color}};"></i>
                </td>
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

          if(this.config.actions){

          }

        }
      }
    })
})();
