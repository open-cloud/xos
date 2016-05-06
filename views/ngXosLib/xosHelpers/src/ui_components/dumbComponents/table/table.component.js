/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 3/24/16.
 */

(function () {
  'use strict';

  angular.module('xos.uiComponents')

    /**
    * @ngdoc directive
    * @name xos.uiComponents.directive:xosTable
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
        ],
        filter: 'field', // can be by `field` or `fulltext`
        order: true // whether to show ordering arrows
    * }
    * ```
    * @param {Array} data The data that should be rendered
    * @element ANY
    * @scope
    * @example

  <example module="sampleTable1">
    <file name="index.html">
      <div ng-controller="SampleCtrl1 as vm">
        <xos-table data="vm.data" config="vm.config"></xos-table>
      </div>
    </file>
    <file name="script.js">
      angular.module('sampleTable1', ['xos.uiComponents'])
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

  <example module="sampleTable2" animations="true">
    <file name="index.html">
      <div ng-controller="SampleCtrl2 as vm">
        <xos-table data="vm.data" config="vm.config"></xos-table>
      </div>
    </file>
    <file name="script.js">
      angular.module('sampleTable2', ['xos.uiComponents', 'ngAnimate'])
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
          ],
          filter: 'field', // can be by `field` or `fulltext`
          order: true
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

  <example module="sampleTable3">
    <file name="index.html">
      <div ng-controller="SampleCtrl3 as vm">
        <xos-table data="vm.data" config="vm.config"></xos-table>
      </div>
    </file>
    <file name="script.js">
      angular.module('sampleTable3', ['xos.uiComponents'])
      .controller('SampleCtrl3', function(){
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
          pagination: {
            pageSize: 2
          }
        };

        this.data = [
          {
            name: 'John',
            lastname: 'Doe'
          },
          {
            name: 'Gili',
            lastname: 'Fereydoun'
          },
          {
            name: 'Lucky',
            lastname: 'Clarkson'
          },
          {
            name: 'Tate',
            lastname: 'Spalding'
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
          <div ng-show="vm.data.length > 0">
            <div class="row" ng-if="vm.config.filter == 'fulltext'">
              <div class="col-xs-12">
                <input
                  class="form-control"
                  placeholder="Type to search.."
                  type="text"
                  ng-model="vm.query"/>
              </div>
            </div>
            <table ng-class="vm.classes" ng-hide="vm.data.length == 0">
              <thead>
                <tr>
                  <th ng-repeat="col in vm.columns">
                    {{col.label}}
                    <span ng-if="vm.config.order">
                      <a href="" ng-click="vm.orderBy = col.prop; vm.reverse = false">
                        <i class="glyphicon glyphicon-chevron-up"></i>
                      </a>
                      <a href="" ng-click="vm.orderBy = col.prop; vm.reverse = true">
                        <i class="glyphicon glyphicon-chevron-down"></i>
                      </a>
                    </span>
                  </th>
                  <th ng-if="vm.config.actions">Actions:</th>
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
                <tr ng-repeat="item in vm.data | filter:vm.query | orderBy:vm.orderBy:vm.reverse | pagination:vm.currentPage * vm.config.pagination.pageSize | limitTo: (vm.config.pagination.pageSize || vm.data.length) track by $index">
                  <td ng-repeat="col in vm.columns">
                    <span ng-if="!col.type">{{item[col.prop]}}</span>
                    <span ng-if="col.type === 'boolean'">
                      <i class="glyphicon"
                        ng-class="{'glyphicon-ok': item[col.prop], 'glyphicon-remove': !item[col.prop]}">
                      </i>
                    </span>
                    <span ng-if="col.type === 'date'">
                      {{item[col.prop] | date:'H:mm MMM d, yyyy'}}
                    </span>
                    <span ng-if="col.type === 'array'">
                      {{item[col.prop] | arrayToList}}
                    </span>
                    <span ng-if="col.type === 'object'">
                      <dl class="dl-horizontal" ng-repeat="(k,v) in item[col.prop]">
                        <dt>{{k}}</dt>
                        <dd>{{v}}</dd>
                      </dl>
                    </span>
                    <span ng-if="col.type === 'custom'">
                      {{col.formatter(item[col.prop])}}
                    </span>
                  </td>
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
            <xos-pagination
              ng-if="vm.config.pagination"
              page-size="vm.config.pagination.pageSize"
              total-elements="vm.data.length"
              change="vm.goToPage">
              </xos-pagination>
          </div>
          <div ng-show="vm.data.length == 0 || !vm.data">
             <xos-alert config="{type: 'info'}">
              No data to show.
            </xos-alert>
          </div>
        `,
        bindToController: true,
        controllerAs: 'vm',
        controller: function(_){

          if(!this.config){
            throw new Error('[xosTable] Please provide a configuration via the "config" attribute');
          }

          if(!this.config.columns){
            throw new Error('[xosTable] Please provide a columns list in the configuration');
          }

          // if columns with type 'custom' are provide
          // check that a custom formatted is provided too
          let customCols = _.filter(this.config.columns, {type: 'custom'});
          if(angular.isArray(customCols) && customCols.length > 0){
            _.forEach(customCols, (col) => {
              if(!col.formatter){
                throw new Error('[xosTable] You have provided a custom field type, a formatter function should provided too.');
              }
            })
          }

          this.columns = this.config.columns;
          this.classes = this.config.classes || 'table table-striped table-bordered';

          if(this.config.actions){
            // TODO validate action format
          }
          if(this.config.pagination){
            this.currentPage = 0;
            this.goToPage = (n) => {
              this.currentPage = n;
            };
          }

        }
      }
    })
.filter('arrayToList', function(){
  return (input) => {
    if(!angular.isArray(input)){
      return input;
    }
    return input.join(', ');
  }
});
})();
