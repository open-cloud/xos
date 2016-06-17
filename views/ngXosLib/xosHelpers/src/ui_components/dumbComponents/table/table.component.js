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
    *       prop: 'Property to read in the model object',
    *       type: 'boolean'| 'array'| 'object'| 'custom'| 'date' | 'icon' // see examples for more details
            formatter: fn(), // receive the whole item if tipe is custom and return a string
            link: fn() // receive the whole item and return an url
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
        order: true | {field: 'property name', reverse: true | false} // whether to show ordering arrows, or a configuration for a default ordering
    * }
    * ```
    * @param {Array} data The data that should be rendered
    * @element ANY
    * @scope
    * @example
  
  # Basic usage
  <example module="sampleTable1">
    <file name="index.html">
      <div ng-controller="SampleCtrl1 as vm">
        <xos-table data="vm.data" config="vm.config"></xos-table>
      </div>
    </file>
    <file name="script.js">
      angular.module('sampleTable1', ['xos.uiComponents'])
      .factory('_', function($window){
        return $window._;
      })
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
  
  # Filtering
  <example module="sampleTable2" animations="true">
    <file name="index.html">
      <div ng-controller="SampleCtrl2 as vm">
        <xos-table data="vm.data" config="vm.config"></xos-table>
      </div>
    </file>
    <file name="script.js">
      angular.module('sampleTable2', ['xos.uiComponents', 'ngAnimate'])
      .factory('_', function($window){
        return $window._;
      })
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
  
  # Pagination
  <example module="sampleTable3">
    <file name="index.html">
      <div ng-controller="SampleCtrl3 as vm">
        <xos-table data="vm.data" config="vm.config"></xos-table>
      </div>
    </file>
    <file name="script.js">
      angular.module('sampleTable3', ['xos.uiComponents'])
      .factory('_', function($window){
        return $window._;
      })
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
  
  # Field formatter
  <example module="sampleTable4">
    <file name="index.html">
      <div ng-controller="SampleCtrl as vm">
        <xos-table data="vm.data" config="vm.config"></xos-table>
      </div>
    </file>
    <file name="script.js">
      angular.module('sampleTable4', ['xos.uiComponents'])
      .factory('_', function($window){
        return $window._;
      })
      .controller('SampleCtrl', function(){
        this.config = {
          columns: [
            {
              label: 'First Name',
              prop: 'name',
              link: item => `https://www.google.it/#q=${item.name}`
            },
            {
              label: 'Enabled',
              prop: 'enabled',
              type: 'boolean'
            },
            {
              label: 'Services',
              prop: 'services',
              type: 'array'
            },
            {
              label: 'Details',
              prop: 'details',
              type: 'object'
            },
            {
              label: 'Created',
              prop: 'created',
              type: 'date'
            },
            {
              label: 'Icon',
              type: 'icon',
              formatter: item => item.icon //note that this refer to [Bootstrap Glyphicon](http://getbootstrap.com/components/#glyphicons)
            }
          ]
        };

        this.data = [
          {
            name: 'John',
            enabled: true,
            services: ['Cdn', 'IpTv'],
            details: {
              c_tag: '243',
              s_tag: '444'
            },
            created: new Date('December 17, 1995 03:24:00'),
            icon: 'music'
          },
          {
            name: 'Gili',
            enabled: false,
            services: ['Cdn', 'IpTv', 'Cache'],
            details: {
              c_tag: '675',
              s_tag: '893'
            },
            created: new Date(),
            icon: 'camera'
          }
        ]
      });
    </file>
  </example>

  # Custom formatter
  <example module="sampleTable5">
    <file name="index.html">
      <div ng-controller="SampleCtrl as vm">
        <xos-table data="vm.data" config="vm.config"></xos-table>
      </div>
    </file>
    <file name="script.js">
      angular.module('sampleTable5', ['xos.uiComponents'])
      .factory('_', function($window){
        return $window._;
      })
      .controller('SampleCtrl', function(){
        this.config = {
          columns: [
            {
              label: 'Username',
              prop: 'username'
            },
            {
              label: 'Features',
              type: 'custom',
              formatter: (val) => {
                
                let cdnEnabled = val.features.cdn ? 'enabled' : 'disabled';
                return `
                  Cdn is ${cdnEnabled},
                  uplink speed is ${val.features.uplink_speed}
                  and downlink speed is ${val.features.downlink_speed}
                `;
              }
            }
          ]
        };

        this.data = [
          {
            username: 'John',
            features: {
              "cdn": false,
              "uplink_speed": 1000000000,
              "downlink_speed": 1000000000,
              "uverse": true,
              "status": "enabled"
            }
          },
          {
            username: 'Gili',
            features: {
              "cdn": true,
              "uplink_speed": 3000000000,
              "downlink_speed": 2000000000,
              "uverse": true,
              "status": "enabled"
            }
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
          <div ng-show="vm.data.length > 0 && vm.loader == false">
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
                      ng-if="col.type !== 'boolean' && col.type !== 'array' && col.type !== 'object' && col.type !== 'custom'"
                      class="form-control"
                      placeholder="Type to search by {{col.label}}"
                      type="text"
                      ng-model="vm.query[col.prop]"/>
                    <select
                      ng-if="col.type === 'boolean'"
                      class="form-control"
                      ng-model="vm.query[col.prop]">
                      <option value="">-</option>
                      <option value="true">True</option>
                      <option value="false">False</option>
                    </select>
                  </td>
                  <td ng-if="vm.config.actions"></td>
                </tr>
              </tbody>
              <tbody>
                <tr ng-repeat="item in vm.data | filter:vm.query:vm.comparator | orderBy:vm.orderBy:vm.reverse | pagination:vm.currentPage * vm.config.pagination.pageSize | limitTo: (vm.config.pagination.pageSize || vm.data.length) track by $index">
                  <td ng-repeat="col in vm.columns" xos-link-wrapper>
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
                      <dl class="dl-horizontal">
                        <span ng-repeat="(k,v) in item[col.prop]">
                          <dt>{{k}}</dt>
                          <dd>{{v}}</dd>
                        </span>
                      </dl>
                    </span>
                    <span ng-if="col.type === 'custom'">
                      {{col.formatter(item)}}
                    </span>
                    <span ng-if="col.type === 'icon'">
                      <i class="glyphicon glyphicon-{{col.formatter(item)}}">
                      </i>
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
          <div ng-show="(vm.data.length == 0 || !vm.data) && vm.loader == false">
             <xos-alert config="{type: 'info'}">
              No data to show.
            </xos-alert>
          </div>
          <div ng-show="vm.loader == true">
            <div class="loader"></div>
          </div>
        `,
        bindToController: true,
        controllerAs: 'vm',
        controller: function(_, $scope, Comparator){

          this.comparator = Comparator;

          this.loader = true;

          $scope.$watch(() => this.data, data => {
            if(angular.isDefined(data)){
              this.loader = false;
            }
          });

          if(!this.config){
            throw new Error('[xosTable] Please provide a configuration via the "config" attribute');
          }

          if(!this.config.columns){
            throw new Error('[xosTable] Please provide a columns list in the configuration');
          }

          // handle default ordering
          if(this.config.order && angular.isObject(this.config.order)){
            this.reverse = this.config.order.reverse || false;
            this.orderBy = this.config.order.field || 'id';
          }

          // if columns with type 'custom' are provided
          // check that a custom formatte3 is provided too
          let customCols = _.filter(this.config.columns, {type: 'custom'});
          if(angular.isArray(customCols) && customCols.length > 0){
            _.forEach(customCols, (col) => {
              if(!col.formatter || !angular.isFunction(col.formatter)){
                throw new Error('[xosTable] You have provided a custom field type, a formatter function should provided too.');
              }
            })
          }

          // if columns with type 'icon' are provided
          // check that a custom formatte3 is provided too
          let iconCols = _.filter(this.config.columns, {type: 'icon'});
          if(angular.isArray(iconCols) && iconCols.length > 0){
            _.forEach(iconCols, (col) => {
              if(!col.formatter || !angular.isFunction(col.formatter)){
                throw new Error('[xosTable] You have provided an icon field type, a formatter function should provided too.');
              }
            })
          }

          // if a link property is passed,
          // it should be a function
          let linkedColumns = _.filter(this.config.columns, col => angular.isDefined(col.link));
          if(angular.isArray(linkedColumns) && linkedColumns.length > 0){
            _.forEach(linkedColumns, (col) => {
              if(!angular.isFunction(col.link)){
                throw new Error('[xosTable] The link property should be a function.');
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
    // TODO move in separate files
    // TODO test
    .filter('arrayToList', function(){
      return (input) => {
        if(!angular.isArray(input)){
          return input;
        }
        return input.join(', ');
      }
    })
    // TODO test
    .directive('xosLinkWrapper', function() {
      return {
        restrict: 'A',
        transclude: true,
        template: `
          <a ng-if="col.link" href="{{col.link(item)}}">
            <div ng-transclude></div>
          </a>
          <div ng-transclude ng-if="!col.link"></div>
        `
      };
    });
})();
