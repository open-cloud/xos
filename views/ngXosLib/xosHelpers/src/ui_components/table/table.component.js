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
    * @param {Object} config The configuration for the component.
    * ```
    * {
    *   columns: [
    *     {
    *       label: 'Human readable name',
    *       prop: 'Property to read in the model object'
    *     }
    *   ],
    *   classes: 'table table-striped table-bordered',
    *   actions: [ // if defined add an action column
          {
            label: 'delete',
            icon: 'remove', // refers to bootstraps glyphicon
            cb: (user) => { // receive the model
              console.log(user);
            },
            color: 'red'
          }
        ]
    * }
    * ```
    * @param {Array} data The data that should be rendered
    * @element ANY
    * @scope
    * @example

  <example module="sampleModule1">
    <file name="index.html">
      <div ng-controller="SampleCtrl1 as vm">
        <xos-table data="vm.data" config="vm.config"></xos-table>
      </div>
    </file>
    <file name="script.js">
      angular.module('sampleModule1', ['xos.uiComponents.table'])
      .controller('SampleCtrl1', function(){
        this.config = {
          columns: [
            {
              label: 'First Name', // column title
              prop: 'name' // property to read in the data array
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
      </div>
    </file>
    <file name="script.js">
      angular.module('sampleModule2', ['xos.uiComponents.table'])
      .controller('SampleCtrl2', function(){
        this.config = {
          columns: [
            {
              label: 'First Name', // column title
              prop: 'name' // property to read in the data array
            },
            {
              label: 'Last Name',
              prop: 'lastname'
            }
          ],
          classes: 'table table-striped table-condensed', // table classes, default to `table table-striped table-bordered`
          actions: [ // if defined add an action column
            {
              label: 'delete', // label
              icon: 'remove', // icons, refers to bootstraps glyphicon
              cb: (user) => { // callback, get feeded with the full object
                console.log(user);
              },
              color: 'red' // icon color
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
          <div class="row" ng-if="vm.config.filter == 'fulltext'">
            <div class="col-xs-12">
              <input
                class="form-control"
                placeholder="Type to search.."
                type="text"
                ng-model="vm.query"/>
            </div>
          </div>
          <table ng-class="vm.classes" ng-show="vm.data.length > 0">
            <thead>
              <tr>
                <th ng-repeat="col in vm.columns">{{col.label}}</th>
                <th ng-if="vm.config.actions">Actions</th>
              </tr>
            </thead>
            <tbody ng-if="vm.config.filter == 'field'">
              <tr>
                <td ng-repeat="col in vm.columns">
                  <input
                    class="form-control"
                    placeholder="Type to search by {{col.label}}"
                    type="text"
                    ng-model="vm.query[col.prop]"/>
                </td>
                <td ng-if="vm.config.actions"></td>
              </tr>
            </tbody>
            <tbody>
              <tr ng-repeat="item in vm.data | filter:vm.query">
                <td ng-repeat="col in vm.columns">{{item[col.prop]}}</td>
                <td ng-if="vm.config.actions">
                  <a href=""
                    ng-repeat="action in vm.config.actions"
                    ng-click="action.cb(item)"
                    title="{{action.label}}">
                    <i
                      class="glyphicon glyphicon-{{action.icon}}"
                      style="color: {{action.color}};"></i>
                  </a>
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
