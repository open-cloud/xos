'use strict';

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
  * @name xos.uiComponents
  * @description
  * A collection of UI components useful for Dashboard development.
  * Currently available components are:
  * - [xosAlert](/#/module/xos.uiComponents.directive:xosAlert)
  * - [xosForm](/#/module/xos.uiComponents.directive:xosForm)
  * - [xosPagination](/#/module/xos.uiComponents.directive:xosPagination)
  * - [xosSmartTable](/#/module/xos.uiComponents.directive:xosSmartTable)
  * - [xosTable](/#/module/xos.uiComponents.directive:xosTable)
  * - [xosValidation](/#/module/xos.uiComponents.directive:xosValidation)
  **/

  angular.module('xos.uiComponents', ['chart.js', 'RecursionHelper']);
})();
//# sourceMappingURL=../maps/ui_components/ui-components.module.js.map

'use strict';

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol ? "symbol" : typeof obj; };

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
  * @name xos.uiComponents.directive:xosSmartTable
  * @link xos.uiComponents.directive:xosTable xosTable
  * @link xos.uiComponents.directive:xosForm xosForm
  * @restrict E
  * @description The xos-table directive
  * @param {Object} config The configuration for the component,
  * it is composed by the name of an angular [$resource](https://docs.angularjs.org/api/ngResource/service/$resource)
  * and an array of fields that shouldn't be printed.
  * ```
  * {
      resource: 'Users',
      hiddenFields: []
    }
  * ```
  * @scope
  * @example
    <example module="sampleSmartTable">
    <file name="index.html">
      <div ng-controller="SampleCtrl as vm">
        <xos-smart-table config="vm.config"></xos-smart-table>
      </div>
    </file>
    <file name="script.js">
      angular.module('sampleSmartTable', ['xos.uiComponents', 'ngResource', 'ngMockE2E'])
      // This is only for documentation purpose
      .run(function($httpBackend, _){
        let datas = [{id: 1, name: 'Jhon', surname: 'Doe'}];
        let count = 1;
          let paramsUrl = new RegExp(/\/test\/(.+)/);
          $httpBackend.whenDELETE(paramsUrl, undefined, ['id']).respond((method, url, data, headers, params) => {
          data = angular.fromJson(data);
          let id = url.match(paramsUrl)[1];
          _.remove(datas, (d) => {
            return d.id === parseInt(id);
          })
          return [204];
        });
          $httpBackend.whenGET('/test').respond(200, datas)
        $httpBackend.whenPOST('/test').respond((method, url, data) => {
          data = angular.fromJson(data);
          data.id = ++count;
          datas.push(data);
          return [201, data, {}];
        });
      })
      .factory('_', function($window){
        return $window._;
      })
      .service('SampleResource', function($resource){
        return $resource('/test/:id', {id: '@id'});
      })
      // End of documentation purpose, example start
      .controller('SampleCtrl', function(){
        this.config = {
          resource: 'SampleResource'
        };
      });
    </file>
  </example>
  */

  .directive('xosSmartTable', function () {
    return {
      restrict: 'E',
      scope: {
        config: '='
      },
      template: '\n        <div class="row" ng-show="vm.data.length > 0">\n          <div class="col-xs-12 text-right">\n            <a href="" class="btn btn-success" ng-click="vm.createItem()">\n              Add\n            </a>\n          </div>\n        </div>\n        <div class="row">\n          <div class="col-xs-12 table-responsive">\n            <xos-table config="vm.tableConfig" data="vm.data"></xos-table>\n          </div>\n        </div>\n        <div class="panel panel-default" ng-show="vm.detailedItem">\n          <div class="panel-heading">\n            <div class="row">\n              <div class="col-xs-11">\n                <h3 class="panel-title" ng-show="vm.detailedItem.id">Update {{vm.config.resource}} {{vm.detailedItem.id}}</h3>\n                <h3 class="panel-title" ng-show="!vm.detailedItem.id">Create {{vm.config.resource}} item</h3>\n              </div>\n              <div class="col-xs-1">\n                <a href="" ng-click="vm.cleanForm()">\n                  <i class="glyphicon glyphicon-remove pull-right"></i>\n                </a>\n              </div>\n            </div>\n          </div>\n          <div class="panel-body">\n            <xos-form config="vm.formConfig" ng-model="vm.detailedItem"></xos-form>\n          </div>\n        </div>\n        <xos-alert config="{type: \'success\', closeBtn: true}" show="vm.responseMsg">{{vm.responseMsg}}</xos-alert>\n        <xos-alert config="{type: \'danger\', closeBtn: true}" show="vm.responseErr">{{vm.responseErr}}</xos-alert>\n      ',
      bindToController: true,
      controllerAs: 'vm',
      controller: ["$injector", "LabelFormatter", "_", "XosFormHelpers", function controller($injector, LabelFormatter, _, XosFormHelpers) {
        var _this = this;

        // TODO
        // - Validate the config (what if resource does not exist?)

        // NOTE
        // Corner case
        // - if response is empty, how can we generate a form ?

        this.responseMsg = false;
        this.responseErr = false;

        this.tableConfig = {
          columns: [],
          actions: [{
            label: 'delete',
            icon: 'remove',
            cb: function cb(item) {
              _this.Resource.delete({ id: item.id }).$promise.then(function () {
                _.remove(_this.data, function (d) {
                  return d.id === item.id;
                });
                _this.responseMsg = _this.config.resource + ' with id ' + item.id + ' successfully deleted';
              }).catch(function (err) {
                _this.responseErr = err.data.detail || 'Error while deleting ' + _this.config.resource + ' with id ' + item.id;
              });
            },
            color: 'red'
          }, {
            label: 'details',
            icon: 'search',
            cb: function cb(item) {
              _this.detailedItem = item;
            }
          }],
          classes: 'table table-striped table-bordered table-responsive',
          filter: 'field',
          order: true,
          pagination: {
            pageSize: 10
          }
        };

        this.formConfig = {
          exclude: this.config.hiddenFields,
          fields: {},
          formName: this.config.resource + 'Form',
          actions: [{
            label: 'Save',
            icon: 'ok',
            cb: function cb(item) {
              var p = void 0;
              var isNew = true;

              if (item.id) {
                p = item.$update();
                isNew = false;
              } else {
                p = item.$save();
              }

              p.then(function (res) {
                if (isNew) {
                  _this.data.push(angular.copy(res));
                }
                delete _this.detailedItem;
                _this.responseMsg = _this.config.resource + ' with id ' + item.id + ' successfully saved';
              }).catch(function (err) {
                _this.responseErr = err.data.detail || 'Error while saving ' + _this.config.resource + ' with id ' + item.id;
              });
            },
            class: 'success'
          }]
        };

        this.cleanForm = function () {
          delete _this.detailedItem;
        };

        this.createItem = function () {
          _this.detailedItem = new _this.Resource();
        };

        this.Resource = $injector.get(this.config.resource);

        var getData = function getData() {
          _this.Resource.query().$promise.then(function (res) {

            if (!res[0]) {
              return;
            }

            var item = res[0];
            var props = Object.keys(item);

            _.remove(props, function (p) {
              return p === 'id' || p === 'validators';
            });

            // TODO move out cb,  non sense triggering a lot of times
            if (angular.isArray(_this.config.hiddenFields)) {
              props = _.difference(props, _this.config.hiddenFields);
            }

            var labels = props.map(function (p) {
              return LabelFormatter.format(p);
            });

            props.forEach(function (p, i) {
              var fieldConfig = {
                label: labels[i],
                prop: p
              };

              if (typeof item[p] !== 'string' && typeof item[p] !== 'undefined') {
                fieldConfig.type = _typeof(item[p]);
              }

              _this.tableConfig.columns.push(fieldConfig);
            });

            // build form structure
            // TODO move in a pure function for testing purposes
            props.forEach(function (p, i) {
              _this.formConfig.fields[p] = {
                label: LabelFormatter.format(labels[i]).replace(':', ''),
                type: XosFormHelpers._getFieldFormat(item[p])
              };
            });

            _this.data = res;
          });
        };

        getData();
      }]
    };
  });
})();
//# sourceMappingURL=../../../maps/ui_components/smartComponents/smartTable/smartTable.component.js.map

'use strict';

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
    * @name xos.uiComponents.directive:xosSmartPie
    * @restrict E
    * @description The xos-table directive
    * @param {Object} config The configuration for the component,
    * it is composed by the name of an angular [$resource](https://docs.angularjs.org/api/ngResource/service/$resource)
    * and a field name that is used to group the data.
    * ```
    * {
        resource: 'Users',
        groupBy: 'fieldName',
        classes: 'my-custom-class',
        labelFormatter: (labels) => {
          // here you can format your label,
          // you should return an array with the same order
          return labels;
        }
      }
    * ```
    * @scope
    * @example
    
    Displaying Local data
      <example module="sampleSmartPieLocal">
      <file name="index.html">
        <div ng-controller="SampleCtrlLocal as vm">
          <xos-smart-pie config="vm.configLocal"></xos-smart-pie>
        </div>
      </file>
      <file name="script.js">
        angular.module('sampleSmartPieLocal', ['xos.uiComponents'])
        .factory('_', function($window){
          return $window._;
        })
        .controller('SampleCtrlLocal', function($timeout){
          
          this.datas = [
            {id: 1, first_name: 'Jon', last_name: 'aaa', category: 2},
            {id: 2, first_name: 'Danaerys', last_name: 'Targaryen', category: 1},
            {id: 3, first_name: 'Aria', last_name: 'Stark', category: 2}
          ];
            this.configLocal = {
            data: [],
            groupBy: 'category',
            classes: 'local',
            labelFormatter: (labels) => {
              return labels.map(l => l === '1' ? 'North' : 'Dragon');
            }
          };
          
          $timeout(() => {
            // this need to be triggered in this way just because of ngDoc,
            // otherwise you can assign data directly in the config
            this.configLocal.data = this.datas;
          }, 1)
        });
      </file>
    </example>
      Fetching data from API
      <example module="sampleSmartPieResource">
      <file name="index.html">
        <div ng-controller="SampleCtrl as vm">
          <xos-smart-pie config="vm.config"></xos-smart-pie>
        </div>
      </file>
      <file name="script.js">
        angular.module('sampleSmartPieResource', ['xos.uiComponents', 'ngResource', 'ngMockE2E'])
        .controller('SampleCtrl', function(){
          this.config = {
            resource: 'SampleResource',
            groupBy: 'category',
            classes: 'resource',
            labelFormatter: (labels) => {
              return labels.map(l => l === '1' ? 'North' : 'Dragon');
            }
          };
        });
      </file>
      <file name="backendPoll.js">
        angular.module('sampleSmartPieResource')
        .run(function($httpBackend, _){
          let datas = [
            {id: 1, first_name: 'Jon', last_name: 'Snow', category: 1},
            {id: 2, first_name: 'Danaerys', last_name: 'Targaryen', category: 2},
            {id: 3, first_name: 'Aria', last_name: 'Stark', category: 1}
          ];
            $httpBackend.whenGET('/test').respond(200, datas)
        })
        .factory('_', function($window){
          return $window._;
        })
        .service('SampleResource', function($resource){
          return $resource('/test/:id', {id: '@id'});
        })
      </file>
    </example>
      Polling data from API
      <example module="sampleSmartPiePoll">
      <file name="index.html">
        <div ng-controller="SampleCtrl as vm">
          <xos-smart-pie config="vm.config"></xos-smart-pie>
        </div>
      </file>
      <file name="script.js">
        angular.module('sampleSmartPiePoll', ['xos.uiComponents', 'ngResource', 'ngMockE2E'])
        .controller('SampleCtrl', function(){
          this.config = {
            resource: 'SampleResource',
            groupBy: 'category',
            poll: 2,
            labelFormatter: (labels) => {
              return labels.map(l => l === '1' ? 'Active' : 'Banned');
            }
          };
        });
      </file>
      <file name="backend.js">
        angular.module('sampleSmartPiePoll')
        .run(function($httpBackend, _){
          let mock = [
            [
              {id: 1, first_name: 'Jon', last_name: 'Snow', category: 1},
              {id: 2, first_name: 'Danaerys', last_name: 'Targaryen', category: 2},
              {id: 3, first_name: 'Aria', last_name: 'Stark', category: 1},
              {id: 3, first_name: 'Tyrion', last_name: 'Lannister', category: 1}
            ],
              [
              {id: 1, first_name: 'Jon', last_name: 'Snow', category: 1},
              {id: 2, first_name: 'Danaerys', last_name: 'Targaryen', category: 2},
              {id: 3, first_name: 'Aria', last_name: 'Stark', category: 2},
              {id: 3, first_name: 'Tyrion', last_name: 'Lannister', category: 2}
            ],
              [
              {id: 1, first_name: 'Jon', last_name: 'Snow', category: 1},
              {id: 2, first_name: 'Danaerys', last_name: 'Targaryen', category: 2},
              {id: 3, first_name: 'Aria', last_name: 'Stark', category: 1},
              {id: 3, first_name: 'Tyrion', last_name: 'Lannister', category: 2}
            ]
          ];
          $httpBackend.whenGET('/test').respond(function(method, url, data, headers, params) {
            return [200, mock[Math.round(Math.random() * 3)]];
          });
        })
        .factory('_', function($window){
          return $window._;
        })
        .service('SampleResource', function($resource){
          return $resource('/test/:id', {id: '@id'});
        })
      </file>
    </example>
    */
  .directive('xosSmartPie', function () {
    return {
      restrict: 'E',
      scope: {
        config: '='
      },
      template: '\n        <canvas\n          class="chart chart-pie {{vm.config.classes}}"\n          chart-data="vm.data" chart-labels="vm.labels"\n          chart-legend="{{vm.config.legend}}">\n        </canvas>\n      ',
      bindToController: true,
      controllerAs: 'vm',
      controller: ["$injector", "$interval", "$scope", "$timeout", "_", function controller($injector, $interval, $scope, $timeout, _) {
        var _this = this;

        if (!this.config.resource && !this.config.data) {
          throw new Error('[xosSmartPie] Please provide a resource or an array of data in the configuration');
        }

        var groupData = function groupData(data) {
          return _.groupBy(data, _this.config.groupBy);
        };
        var formatData = function formatData(data) {
          return _.reduce(Object.keys(data), function (list, group) {
            return list.concat(data[group].length);
          }, []);
        };
        var formatLabels = function formatLabels(data) {
          return angular.isFunction(_this.config.labelFormatter) ? _this.config.labelFormatter(Object.keys(data)) : Object.keys(data);
        };

        var prepareData = function prepareData(data) {
          // group data
          var grouped = groupData(data);
          _this.data = formatData(grouped);
          // create labels
          _this.labels = formatLabels(grouped);
        };

        if (this.config.resource) {
          (function () {

            _this.Resource = $injector.get(_this.config.resource);
            var getData = function getData() {
              _this.Resource.query().$promise.then(function (res) {

                if (!res[0]) {
                  return;
                }

                prepareData(res);
              });
            };

            getData();

            if (_this.config.poll) {
              $interval(function () {
                getData();
              }, _this.config.poll * 1000);
            }
          })();
        } else {
          $scope.$watch(function () {
            return _this.config.data;
          }, function (data) {
            if (data) {
              prepareData(_this.config.data);
            }
          }, true);
        }

        $scope.$on('create', function (event, chart) {
          console.log('create: ' + chart.id);
        });

        $scope.$on('destroy', function (event, chart) {
          console.log('destroy: ' + chart.id);
        });
      }]
    };
  });
})();
//# sourceMappingURL=../../../maps/ui_components/smartComponents/smartPie/smartPie.component.js.map

'use strict';

/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 4/15/16.
 */

(function () {
  'use strict';

  angular.module('xos.uiComponents')

  /**
    * @ngdoc directive
    * @name xos.uiComponents.directive:xosValidation
    * @restrict E
    * @description The xos-validation directive
    * @param {Object} errors The error object
    * @element ANY
    * @scope
  * @example
  <example module="sampleValidation">
    <file name="index.html">
      <div ng-controller="SampleCtrl as vm">
        <div class="row">
          <div class="col-xs-12">
            <label>Set an error type:</label>
          </div>
          <div class="col-xs-2">
            <a class="btn"
              ng-click="vm.field.$error.required = !vm.field.$error.required"
              ng-class="{'btn-default': !vm.field.$error.required, 'btn-success': vm.field.$error.required}">
              Required
            </a>
          </div>
          <div class="col-xs-2">
            <a class="btn"
              ng-click="vm.field.$error.email = !vm.field.$error.email"
              ng-class="{'btn-default': !vm.field.$error.email, 'btn-success': vm.field.$error.email}">
              Email
            </a>
          </div>
          <div class="col-xs-2">
            <a class="btn"
              ng-click="vm.field.$error.minlength = !vm.field.$error.minlength"
              ng-class="{'btn-default': !vm.field.$error.minlength, 'btn-success': vm.field.$error.minlength}">
              Min Length
            </a>
          </div>
          <div class="col-xs-2">
            <a class="btn"
              ng-click="vm.field.$error.maxlength = !vm.field.$error.maxlength"
              ng-class="{'btn-default': !vm.field.$error.maxlength, 'btn-success': vm.field.$error.maxlength}">
              Max Length
            </a>
          </div>
        </div>
        <xos-validation field ="vm.field" form = "vm.form"></xos-validation>
      </div>
    </file>
    <file name="script.js">
      angular.module('sampleValidation', ['xos.uiComponents'])
      .controller('SampleCtrl', function(){
        this.field = {
          $error: {}
        };
        this.form= {
        $submitted:true
        }
      });
    </file>
  </example>
    */

  .directive('xosValidation', function () {
    return {
      restrict: 'E',
      scope: {
        field: '=',
        form: '='
      },
      template: '\n        <div ng-cloak>\n          <xos-alert config="vm.config" show="vm.field.$error.required !== undefined && vm.field.$error.required !== false  && (vm.field.$touched || vm.form.$submitted)">\n            Field required\n          </xos-alert>\n          <xos-alert config="vm.config" show="vm.field.$error.email !== undefined && vm.field.$error.email !== false && (vm.field.$touched || vm.form.$submitted)">\n            This is not a valid email\n          </xos-alert>\n          <xos-alert config="vm.config" show="vm.field.$error.minlength !== undefined && vm.field.$error.minlength !== false && (vm.field.$touched || vm.form.$submitted)">\n            Too short\n          </xos-alert>\n          <xos-alert config="vm.config" show="vm.field.$error.maxlength !== undefined && vm.field.$error.maxlength !== false && (vm.field.$touched || vm.form.$submitted)">\n            Too long\n          </xos-alert>\n          <xos-alert config="vm.config" show="vm.field.$error.custom !== undefined && vm.field.$error.custom !== false && (vm.field.$touched || vm.form.$submitted)">\n            Field invalid\n          </xos-alert>\n        </div>\n      ',
      transclude: true,
      bindToController: true,
      controllerAs: 'vm',
      controller: function controller() {
        this.config = {
          type: 'danger'
        };
      }
    };
  });
})();
//# sourceMappingURL=../../../maps/ui_components/dumbComponents/validation/validation.component.js.map

'use strict';

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

  .directive('xosTable', function () {
    return {
      restrict: 'E',
      scope: {
        data: '=',
        config: '='
      },
      template: '\n          <div ng-show="vm.data.length > 0">\n            <div class="row" ng-if="vm.config.filter == \'fulltext\'">\n              <div class="col-xs-12">\n                <input\n                  class="form-control"\n                  placeholder="Type to search.."\n                  type="text"\n                  ng-model="vm.query"/>\n              </div>\n            </div>\n            <table ng-class="vm.classes" ng-hide="vm.data.length == 0">\n              <thead>\n                <tr>\n                  <th ng-repeat="col in vm.columns">\n                    {{col.label}}\n                    <span ng-if="vm.config.order">\n                      <a href="" ng-click="vm.orderBy = col.prop; vm.reverse = false">\n                        <i class="glyphicon glyphicon-chevron-up"></i>\n                      </a>\n                      <a href="" ng-click="vm.orderBy = col.prop; vm.reverse = true">\n                        <i class="glyphicon glyphicon-chevron-down"></i>\n                      </a>\n                    </span>\n                  </th>\n                  <th ng-if="vm.config.actions">Actions:</th>\n                </tr>\n              </thead>\n              <tbody ng-if="vm.config.filter == \'field\'">\n                <tr>\n                  <td ng-repeat="col in vm.columns">\n                    <input\n                      ng-if="col.type !== \'boolean\'"\n                      class="form-control"\n                      placeholder="Type to search by {{col.label}}"\n                      type="text"\n                      ng-model="vm.query[col.prop]"/>\n                    <select\n                      ng-if="col.type === \'boolean\'"\n                      class="form-control"\n                      ng-model="vm.query[col.prop]">\n                      <option value="">-</option>\n                      <option value="true">True</option>\n                      <option value="false">False</option>\n                    </select>\n                  </td>\n                  <td ng-if="vm.config.actions"></td>\n                </tr>\n              </tbody>\n              <tbody>\n                <tr ng-repeat="item in vm.data | filter:vm.query | orderBy:vm.orderBy:vm.reverse | pagination:vm.currentPage * vm.config.pagination.pageSize | limitTo: (vm.config.pagination.pageSize || vm.data.length) track by $index">\n                  <td ng-repeat="col in vm.columns" link-wrapper>\n                    <span ng-if="!col.type">{{item[col.prop]}}</span>\n                    <span ng-if="col.type === \'boolean\'">\n                      <i class="glyphicon"\n                        ng-class="{\'glyphicon-ok\': item[col.prop], \'glyphicon-remove\': !item[col.prop]}">\n                      </i>\n                    </span>\n                    <span ng-if="col.type === \'date\'">\n                      {{item[col.prop] | date:\'H:mm MMM d, yyyy\'}}\n                    </span>\n                    <span ng-if="col.type === \'array\'">\n                      {{item[col.prop] | arrayToList}}\n                    </span>\n                    <span ng-if="col.type === \'object\'">\n                      <dl class="dl-horizontal">\n                        <span ng-repeat="(k,v) in item[col.prop]">\n                          <dt>{{k}}</dt>\n                          <dd>{{v}}</dd>\n                        </span>\n                      </dl>\n                    </span>\n                    <span ng-if="col.type === \'custom\'">\n                      {{col.formatter(item)}}\n                    </span>\n                    <span ng-if="col.type === \'icon\'">\n                      <i class="glyphicon glyphicon-{{col.formatter(item)}}">\n                      </i>\n                    </span>\n                  </td>\n                  <td ng-if="vm.config.actions">\n                    <a href=""\n                      ng-repeat="action in vm.config.actions"\n                      ng-click="action.cb(item)"\n                      title="{{action.label}}">\n                      <i\n                        class="glyphicon glyphicon-{{action.icon}}"\n                        style="color: {{action.color}};"></i>\n                    </a>\n                  </td>\n                </tr>\n              </tbody>\n            </table>\n            <xos-pagination\n              ng-if="vm.config.pagination"\n              page-size="vm.config.pagination.pageSize"\n              total-elements="vm.data.length"\n              change="vm.goToPage">\n              </xos-pagination>\n          </div>\n          <div ng-show="vm.data.length == 0 || !vm.data">\n             <xos-alert config="{type: \'info\'}">\n              No data to show.\n            </xos-alert>\n          </div>\n        ',
      bindToController: true,
      controllerAs: 'vm',
      controller: ["_", function controller(_) {
        var _this = this;

        if (!this.config) {
          throw new Error('[xosTable] Please provide a configuration via the "config" attribute');
        }

        if (!this.config.columns) {
          throw new Error('[xosTable] Please provide a columns list in the configuration');
        }

        // handle default ordering
        if (this.config.order && angular.isObject(this.config.order)) {
          this.reverse = this.config.order.reverse || false;
          this.orderBy = this.config.order.field || 'id';
        }

        // if columns with type 'custom' are provided
        // check that a custom formatte3 is provided too
        var customCols = _.filter(this.config.columns, { type: 'custom' });
        if (angular.isArray(customCols) && customCols.length > 0) {
          _.forEach(customCols, function (col) {
            if (!col.formatter || !angular.isFunction(col.formatter)) {
              throw new Error('[xosTable] You have provided a custom field type, a formatter function should provided too.');
            }
          });
        }

        // if columns with type 'icon' are provided
        // check that a custom formatte3 is provided too
        var iconCols = _.filter(this.config.columns, { type: 'icon' });
        if (angular.isArray(iconCols) && iconCols.length > 0) {
          _.forEach(iconCols, function (col) {
            if (!col.formatter || !angular.isFunction(col.formatter)) {
              throw new Error('[xosTable] You have provided an icon field type, a formatter function should provided too.');
            }
          });
        }

        // if a link property is passed,
        // it should be a function
        var linkedColumns = _.filter(this.config.columns, function (col) {
          return angular.isDefined(col.link);
        });
        if (angular.isArray(linkedColumns) && linkedColumns.length > 0) {
          _.forEach(linkedColumns, function (col) {
            if (!angular.isFunction(col.link)) {
              throw new Error('[xosTable] The link property should be a function.');
            }
          });
        }

        this.columns = this.config.columns;
        this.classes = this.config.classes || 'table table-striped table-bordered';

        if (this.config.actions) {
          // TODO validate action format
        }
        if (this.config.pagination) {
          this.currentPage = 0;
          this.goToPage = function (n) {
            _this.currentPage = n;
          };
        }
      }]
    };
  })
  // TODO move in separate files
  // TODO test
  .filter('arrayToList', function () {
    return function (input) {
      if (!angular.isArray(input)) {
        return input;
      }
      return input.join(', ');
    };
  })
  // TODO test
  .directive('linkWrapper', function () {
    return {
      restrict: 'A',
      transclude: true,
      template: '\n          <a ng-if="col.link" href="{{col.link(item)}}">\n            <div ng-transclude></div>\n          </a>\n          <div ng-transclude ng-if="!col.link"></div>\n        '
    };
  });
})();
//# sourceMappingURL=../../../maps/ui_components/dumbComponents/table/table.component.js.map

'use strict';

/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 4/15/16.
 */

(function () {
  'use strict';

  angular.module('xos.uiComponents')

  /**
    * @ngdoc directive
    * @name xos.uiComponents.directive:xosPagination
    * @restrict E
    * @description The xos-table directive
    * @param {Number} pageSize Number of elements per page
    * @param {Number} totalElements Number of total elements in the collection
    * @param {Function} change The callback to be triggered on page change.
    * * @element ANY
    * @scope
    * @example
  <example module="samplePagination">
    <file name="index.html">
      <div ng-controller="SampleCtrl1 as vm">
        <xos-pagination
          page-size="vm.pageSize"
          total-elements="vm.totalElements"
          change="vm.change">
        </xos-pagination>
      </div>
    </file>
    <file name="script.js">
      angular.module('samplePagination', ['xos.uiComponents'])
      .controller('SampleCtrl1', function(){
        this.pageSize = 10;
        this.totalElements = 35;
        this.change = (pageNumber) => {
          console.log(pageNumber);
        }
      });
    </file>
  </example>
  **/

  .directive('xosPagination', function () {
    return {
      restrict: 'E',
      scope: {
        pageSize: '=',
        totalElements: '=',
        change: '='
      },
      template: '\n        <div class="row" ng-if="vm.pageList.length > 1">\n          <div class="col-xs-12 text-center">\n            <ul class="pagination">\n              <li\n                ng-click="vm.goToPage(vm.currentPage - 1)"\n                ng-class="{disabled: vm.currentPage == 0}">\n                <a href="" aria-label="Previous">\n                    <span aria-hidden="true">&laquo;</span>\n                </a>\n              </li>\n              <li ng-repeat="i in vm.pageList" ng-class="{active: i === vm.currentPage}">\n                <a href="" ng-click="vm.goToPage(i)">{{i + 1}}</a>\n              </li>\n              <li\n                ng-click="vm.goToPage(vm.currentPage + 1)"\n                ng-class="{disabled: vm.currentPage == vm.pages - 1}">\n                <a href="" aria-label="Next">\n                    <span aria-hidden="true">&raquo;</span>\n                </a>\n              </li>\n            </ul>\n          </div>\n        </div>\n      ',
      bindToController: true,
      controllerAs: 'vm',
      controller: ["$scope", function controller($scope) {
        var _this = this;

        this.currentPage = 0;

        this.goToPage = function (n) {
          if (n < 0 || n === _this.pages) {
            return;
          }
          _this.currentPage = n;
          _this.change(n);
        };

        this.createPages = function (pages) {
          var arr = [];
          for (var i = 0; i < pages; i++) {
            arr.push(i);
          }
          return arr;
        };

        // watch for data changes
        $scope.$watch(function () {
          return _this.totalElements;
        }, function () {
          if (_this.totalElements) {
            _this.pages = Math.ceil(_this.totalElements / _this.pageSize);
            _this.pageList = _this.createPages(_this.pages);
          }
        });
      }]
    };
  }).filter('pagination', function () {
    return function (input, start) {
      if (!input || !angular.isArray(input)) {
        return input;
      }
      start = parseInt(start, 10);
      return input.slice(start);
    };
  });
})();
//# sourceMappingURL=../../../maps/ui_components/dumbComponents/pagination/pagination.component.js.map

'use strict';

/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 4/18/16.
 */

(function () {
  'use strict';

  angular.module('xos.uiComponents')

  /**
    * @ngdoc directive
    * @name xos.uiComponents.directive:xosForm
    * @restrict E
    * @description The xos-form directive.
    * This components have two usage, given a model it is able to autogenerate a form or it can be configured to create a custom form.
    * @param {Object} config The configuration object
    * ```
    * {
    *   exclude: ['id', 'validators', 'created', 'updated', 'deleted'], //field to be skipped in the form, the provide values are concatenated
    *   actions: [ // define the form buttons with related callback
    *     {
            label: 'save',
            icon: 'ok', // refers to bootstraps glyphicon
            cb: (user) => { // receive the model
              console.log(user);
            },
            class: 'success'
          }
    *   ],
    *   fields: {
    *     field_name: {
    *       label: 'Field Label',
    *       type: 'string' // options are: [date, boolean, number, email, string],
    *       validators: {
    *         minlength: number,
              maxlength: number,
              required: boolean,
              min: number,
              max: number
    *       }
    *     }
    *   }
    * }
    * ```
    * @element ANY
    * @scope
    * @requires xos.uiComponents.directive:xosField
    * @requires xos.uiComponents.XosFormHelpers
    * @requires xos.helpers._
    * @example
    
    Autogenerated form
    <example module="sampleForm">
    <file name="script.js">
      angular.module('sampleForm', ['xos.uiComponents'])
      .factory('_', function($window){
        return $window._;
      })
      .controller('SampleCtrl', function(){
        this.model = {
          first_name: 'Jhon',
          last_name: 'Doe',
          email: 'jhon.doe@sample.com',
          active: true,
          birthDate: '2015-02-17T22:06:38.059000Z'
        }
        this.config = {
          exclude: ['password', 'last_login'],
          formName: 'sampleForm',
          actions: [
            {
              label: 'Save',
              icon: 'ok', // refers to bootstraps glyphicon
              cb: (user) => { // receive the model
                console.log(user);
              },
              class: 'success'
            }
          ]
        };
      });
    </file>
    <file name="index.html">
      <div ng-controller="SampleCtrl as vm">
        <xos-form ng-model="vm.model" config="vm.config"></xos-form>
      </div>
    </file>
  </example>
    Configuration defined form
    <example module="sampleForm1">
    <file name="script.js">
      angular.module('sampleForm1', ['xos.uiComponents'])
      .factory('_', function($window){
        return $window._;
      })
      .controller('SampleCtrl1', function(){
        this.model = {
        };
          this.config = {
          exclude: ['password', 'last_login'],
          formName: 'sampleForm1',
          actions: [
            {
              label: 'Save',
              icon: 'ok', // refers to bootstraps glyphicon
              cb: (user) => { // receive the model
                console.log(user);
              },
              class: 'success'
            }
          ],
          fields: {
            first_name: {
              type: 'string',
              validators: {
                required: true
              }
            },
            last_name: {
              label: 'Surname',
              type: 'string',
              validators: {
                required: true,
                minlength: 10
              }
            },
            age: {
              type: 'number',
              validators: {
                required: true,
                min: 21
              }
            },
          }
        };
      });
    </file>
    <file name="index.html">
      <div ng-controller="SampleCtrl1 as vm">
        <xos-form ng-model="vm.model" config="vm.config"></xos-form>
      </div>
    </file>
  </example>
    **/

  .directive('xosForm', function () {
    return {
      restrict: 'E',
      scope: {
        config: '=',
        ngModel: '='
      },
      template: '\n        <form name="vm.{{vm.config.formName || \'form\'}}" novalidate>\n          <div class="form-group" ng-repeat="(name, field) in vm.formField">\n          <!--{{vm.ngModel[name] | json}}-->\n            <xos-field name="name" field="field" ng-model="vm.ngModel[name]"></xos-field>\n            <!--<pre>{{vm[vm.config.formName] || \'form\'  | json }}</pre>-->\n            <!--{{field}}-->\n            <xos-validation field="vm[vm.config.formName || \'form\'][name]" form = "vm[vm.config.formName || \'form\']"></xos-validation>\n            <div class="alert alert-info" ng-show="(field.hint).length >0" role="alert">{{field.hint}}</div>\n          </div>\n          <div class="form-group" ng-if="vm.config.actions">\n            <!--<pre>{{vm.config.feedback}} | json</pre>-->\n\n          <xos-alert config="vm.config.feedback" show="vm.config.feedback.show">{{vm.config.feedback.message}}</xos-alert>\n\n            <button role="button" href=""\n              ng-repeat="action in vm.config.actions"\n              ng-click="action.cb(vm.ngModel, vm[vm.config.formName || \'form\'])"\n              class="btn btn-{{action.class}}"\n              title="{{action.label}}">\n              <i class="glyphicon glyphicon-{{action.icon}}"></i>\n              {{action.label}}\n            </button>\n          </div>\n        </form>\n      ',
      bindToController: true,
      controllerAs: 'vm',
      controller: ["$scope", "$log", "_", "XosFormHelpers", function controller($scope, $log, _, XosFormHelpers) {
        var _this = this;

        if (!this.config) {
          throw new Error('[xosForm] Please provide a configuration via the "config" attribute');
        }

        if (!this.config.actions) {
          throw new Error('[xosForm] Please provide an action list in the configuration');
        }

        if (!this.config.feedback) {
          this.config.feedback = {
            show: false,
            message: 'Form submitted successfully !!!',
            type: 'success'
          };
        }

        this.excludedField = ['id', 'validators', 'created', 'updated', 'deleted', 'backend_status'];
        if (this.config && this.config.exclude) {
          this.excludedField = this.excludedField.concat(this.config.exclude);
        }

        this.formField = [];
        $scope.$watch(function () {
          return _this.config;
        }, function () {

          if (!_this.ngModel) {
            return;
          }
          var diff = _.difference(Object.keys(_this.ngModel), _this.excludedField);
          var modelField = XosFormHelpers.parseModelField(diff);
          _this.formField = XosFormHelpers.buildFormStructure(modelField, _this.config.fields, _this.ngModel);
        }, true);

        $scope.$watch(function () {
          return _this.ngModel;
        }, function (model) {
          // empty from old stuff
          _this.formField = {};
          if (!model) {
            return;
          }
          var diff = _.difference(Object.keys(model), _this.excludedField);
          var modelField = XosFormHelpers.parseModelField(diff);
          _this.formField = XosFormHelpers.buildFormStructure(modelField, _this.config.fields, model);
        });
      }]
    };
  });
})();
//# sourceMappingURL=../../../maps/ui_components/dumbComponents/form/form.component.js.map

'use strict';

/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 5/25/16.
 */

(function () {
  'use strict';

  angular.module('xos.uiComponents')
  /**
    * @ngdoc directive
    * @name xos.uiComponents.directive:xosField
    * @restrict E
    * @description The xos-field directive.
    * This component decide, give a field wich kind of input it need to print.
    * @param {string} name The field name
    * @param {object} field The field configuration:
    * ```
    * {
    *   label: 'Label',
    *   type: 'number', //typeof field
    *   validators: {} // see xosForm for more details
    * }
    * ```
    * @param {mixed} ngModel The field value
    *
    * @example
    
    # Basic Example
    
      <example module="sampleField1">
        <file name="script.js">
          angular.module('sampleField1', ['xos.uiComponents'])
          .factory('_', function($window){
            return $window._;
          })
          .controller('SampleCtrl', function(){
            this.name = 'input-name';
            this.field = {label: 'My String Value:', type: 'string'};
            this.model = 'my string';
          });
        </file>
        <file name="index.html">
          <div ng-controller="SampleCtrl as vm">
            <xos-field ng-model="vm.model" name="vm.name" field="vm.field"></xos-field>
          </div>
        </file>
      </example>
      
      # Possible Values
        <example module="sampleField2">
        <file name="script.js">
          angular.module('sampleField2', ['xos.uiComponents'])
          .factory('_', function($window){
            return $window._;
          })
          .controller('SampleCtrl', function(){
            this.field1 = {
              name: 'number-field',
              field: {label: 'My Number Value:', type: 'number'},
              model: 2
            };
              this.field2 = {
              name: 'date-field',
              field: {label: 'My Date Value:', type: 'date'},
              model: new Date()
            };
              this.field3 = {
              name: 'boolean-field',
              field: {label: 'My Boolean Value:', type: 'boolean'},
              model: true
            };
              this.field4 = {
              name: 'email-field',
              field: {label: 'My Email Value:', type: 'email'},
              model: 'sample@domain.us'
            };
          });
        </file>
        <file name="index.html">
          <div ng-controller="SampleCtrl as vm">
            <xos-field ng-model="vm.field1.model" name="vm.field1.name" field="vm.field1.field"></xos-field>
            <xos-field ng-model="vm.field2.model" name="vm.field2.name" field="vm.field2.field"></xos-field>
            <xos-field ng-model="vm.field3.model" name="vm.field3.name" field="vm.field3.field"></xos-field>
            <xos-field ng-model="vm.field4.model" name="vm.field4.name" field="vm.field4.field"></xos-field>
          </div>
        </file>
      </example>
        # This element is recursive
        <example module="sampleField3">
        <file name="script.js">
          angular.module('sampleField3', ['xos.uiComponents'])
          .factory('_', function($window){
            return $window._;
          })
          .controller('SampleCtrl', function(){
            this.name = 'input-name';
            this.field = {label: 'My Object Value:', type: 'object'};
            this.model = {
              name: 'Jhon',
              age: '25',
              email: 'jhon@thewall.ru',
              active: true
            };
          });
        </file>
        <file name="index.html">
          <div ng-controller="SampleCtrl as vm">
            <xos-field ng-model="vm.model" name="vm.name" field="vm.field"></xos-field>
          </div>
        </file>
      </example>
    */
  .directive('xosField', ["RecursionHelper", function (RecursionHelper) {
    return {
      restrict: 'E',
      scope: {
        name: '=',
        field: '=',
        ngModel: '='
      },
      template: '\n        <label ng-if="vm.field.type !== \'object\'">{{vm.field.label}}</label>\n        <!--<pre>{{vm.field.options[0].id | json}}</pre>-->\n        <!--<pre>{{vm.ngModel | json}}</pre>-->\n            <input\n              ng-if="vm.field.type !== \'boolean\' && vm.field.type !== \'object\' && vm.field.type !== \'select\'"\n              type="{{vm.field.type}}"\n              name="{{vm.name}}"\n              class="form-control"\n              ng-model="vm.ngModel"\n              ng-minlength="vm.field.validators.minlength || 0"\n              ng-maxlength="vm.field.validators.maxlength || 2000"\n              ng-required="vm.field.validators.required || false" />\n              <select class="form-control" ng-if ="vm.field.type === \'select\'"\n                name = "{{vm.name}}"\n                ng-options="item.id as item.label for item in vm.field.options"\n                ng-model="vm.ngModel"\n                ng-required="vm.field.validators.required || false">\n                </select>\n            <span class="boolean-field" ng-if="vm.field.type === \'boolean\'">\n              <a href="#"\n                class="btn btn-success"\n                ng-show="vm.ngModel"\n                ng-click="vm.ngModel = false">\n                <i class="glyphicon glyphicon-ok"></i>\n              </a>\n              <a href="#"\n                class="btn btn-danger"\n                ng-show="!vm.ngModel"\n                ng-click="vm.ngModel = true">\n                <i class="glyphicon glyphicon-remove"></i>\n              </a>\n            </span>\n            <div\n              class="panel panel-default object-field"\n              ng-if="vm.field.type == \'object\' && !vm.isEmptyObject(vm.ngModel)"\n              >\n              <div class="panel-heading">{{vm.field.label}}</div>\n              <div class="panel-body">\n                <div ng-repeat="(k, v) in vm.ngModel">\n                  <xos-field\n                    name="k"\n                    field="{label: vm.formatLabel(k), type: vm.getType(v)}"\n                    ng-model="v">\n                  </xos-field>\n                </div>\n              </div>\n            </div>\n      ',
      bindToController: true,
      controllerAs: 'vm',
      // the compile cicle is needed to support recursion
      compile: function compile(element) {
        return RecursionHelper.compile(element);
      },
      controller: ["$attrs", "XosFormHelpers", "LabelFormatter", function controller($attrs, XosFormHelpers, LabelFormatter) {
        // console.log('Field: ', this.name, this.field, this.ngModel);
        if (!this.name) {
          throw new Error('[xosField] Please provide a field name');
        }
        if (!this.field) {
          throw new Error('[xosField] Please provide a field definition');
        }
        if (!$attrs.ngModel) {
          throw new Error('[xosField] Please provide an ng-model');
        }
        if (this.field.type === 'select' && !this.ngModel) {
          //this.ngModel = this.field.options[0].id;
        }
        this.getType = XosFormHelpers._getFieldFormat;
        this.formatLabel = LabelFormatter.format;

        this.isEmptyObject = function (o) {
          return Object.keys(o).length === 0;
        };
      }]
    };
  }]);
})();
//# sourceMappingURL=../../../maps/ui_components/dumbComponents/field/field.component.js.map

'use strict';

/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 4/15/16.
 */

(function () {
  'use strict';

  angular.module('xos.uiComponents')

  /**
    * @ngdoc directive
    * @name xos.uiComponents.directive:xosAlert
    * @restrict E
    * @description The xos-alert directive
    * @param {Object} config The configuration object
    * ```
    * {
    *   type: 'danger', //info, success, warning
    *   closeBtn: true, //default false
    *   autoHide: 3000 //delay to automatically hide the alert
    * }
    * ```
    * @param {Boolean=} show Binding to show and hide the alert, default to true
    * @element ANY
    * @scope
    * @example
  <example module="sampleAlert1">
    <file name="index.html">
      <div ng-controller="SampleCtrl1 as vm">
        <xos-alert config="vm.config1">
          A sample alert message
        </xos-alert>
        <xos-alert config="vm.config2">
          A sample alert message (with close button)
        </xos-alert>
        <xos-alert config="vm.config3">
          A sample info message
        </xos-alert>
        <xos-alert config="vm.config4">
          A sample success message
        </xos-alert>
        <xos-alert config="vm.config5">
          A sample warning message
        </xos-alert>
      </div>
    </file>
    <file name="script.js">
      angular.module('sampleAlert1', ['xos.uiComponents'])
      .controller('SampleCtrl1', function(){
        this.config1 = {
          type: 'danger'
        };
          this.config2 = {
          type: 'danger',
          closeBtn: true
        };
          this.config3 = {
          type: 'info'
        };
          this.config4 = {
          type: 'success'
        };
          this.config5 = {
          type: 'warning'
        };
      });
    </file>
  </example>
    <example module="sampleAlert2" animations="true">
    <file name="index.html">
      <div ng-controller="SampleCtrl as vm" class="row">
        <div class="col-sm-4">
          <a class="btn btn-default btn-block" ng-show="!vm.show" ng-click="vm.show = true">Show Alert</a>
          <a class="btn btn-default btn-block" ng-show="vm.show" ng-click="vm.show = false">Hide Alert</a>
        </div>
        <div class="col-sm-8">
          <xos-alert config="vm.config1" show="vm.show">
            A sample alert message, not displayed by default.
          </xos-alert>
        </div>
      </div>
    </file>
    <file name="script.js">
      angular.module('sampleAlert2', ['xos.uiComponents', 'ngAnimate'])
      .controller('SampleCtrl', function(){
        this.config1 = {
          type: 'success'
        };
          this.show = false;
      });
    </file>
  </example>
  **/

  .directive('xosAlert', function () {
    return {
      restrict: 'E',
      scope: {
        config: '=',
        show: '=?'
      },
      template: '\n        <div ng-cloak class="alert alert-{{vm.config.type}}" ng-hide="!vm.show">\n          <button type="button" class="close" ng-if="vm.config.closeBtn" ng-click="vm.dismiss()">\n            <span aria-hidden="true">&times;</span>\n          </button>\n          <p ng-transclude></p>\n        </div>\n      ',
      transclude: true,
      bindToController: true,
      controllerAs: 'vm',
      controller: ["$timeout", function controller($timeout) {
        var _this = this;

        if (!this.config) {
          throw new Error('[xosAlert] Please provide a configuration via the "config" attribute');
        }

        // default the value to true
        this.show = this.show !== false;

        this.dismiss = function () {
          _this.show = false;
        };

        if (this.config.autoHide) {
          (function () {
            var to = $timeout(function () {
              _this.dismiss();
              $timeout.cancel(to);
            }, _this.config.autoHide);
          })();
        }
      }]
    };
  });
})();
//# sourceMappingURL=../../../maps/ui_components/dumbComponents/alert/alert.component.js.map

'use strict';

(function () {
  'use strict';

  /**
  * @ngdoc service
  * @name xos.uiComponents.LabelFormatter
  * @description This factory define a set of helper function to format label started from an object property
  **/

  angular.module('xos.uiComponents').factory('LabelFormatter', labelFormatter);

  function labelFormatter() {

    var _formatByUnderscore = function _formatByUnderscore(string) {
      return string.split('_').join(' ').trim();
    };

    var _formatByUppercase = function _formatByUppercase(string) {
      return string.split(/(?=[A-Z])/).map(function (w) {
        return w.toLowerCase();
      }).join(' ');
    };

    var _capitalize = function _capitalize(string) {
      return string.slice(0, 1).toUpperCase() + string.slice(1);
    };

    var format = function format(string) {
      string = _formatByUnderscore(string);
      string = _formatByUppercase(string);

      string = _capitalize(string).replace(/\s\s+/g, ' ') + ':';
      return string.replace('::', ':');
    };

    return {
      // test export
      _formatByUnderscore: _formatByUnderscore,
      _formatByUppercase: _formatByUppercase,
      _capitalize: _capitalize,
      // export to use
      format: format
    };
  }
})();
//# sourceMappingURL=../../../maps/services/helpers/ui/label_formatter.service.js.map

'use strict';

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol ? "symbol" : typeof obj; };

(function () {

  angular.module('xos.uiComponents')

  /**
  * @ngdoc service
  * @name xos.uiComponents.XosFormHelpers
  * @requires xos.uiComponents.LabelFormatter
  * @requires xos.helpers._
  **/

  .service('XosFormHelpers', ["_", "LabelFormatter", function (_, LabelFormatter) {
    var _this = this;

    /**
    * @ngdoc method
    * @name xos.uiComponents.XosFormHelpers#_isEmail
    * @methodOf xos.uiComponents.XosFormHelpers
    * @description
    * Return true if the string is an email address
    * @param {string} text The string to be evaluated
    * @returns {boolean} If the string match an email format
    **/

    this._isEmail = function (text) {
      var re = /(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))/;
      return re.test(text);
    };

    /**
    * @ngdoc method
    * @name xos.uiComponents.XosFormHelpers#_getFieldFormat
    * @methodOf xos.uiComponents.XosFormHelpers
    * @description
    * Return the type of the input
    * @param {mixed} value The data to be evaluated
    * @returns {string} The type of the input
    **/

    this._getFieldFormat = function (value) {

      if (angular.isArray(value)) {
        return 'array';
      }

      // check if is date
      if (_.isDate(value) || !Number.isNaN(Date.parse(value)) && new Date(value).getTime() > 631180800000) {
        return 'date';
      }

      // check if is boolean
      // isNaN(false) = false, false is a number (0), true is a number (1)
      if (typeof value === 'boolean') {
        return 'boolean';
      }

      // check if a string is an email
      if (_this._isEmail(value)) {
        return 'email';
      }

      // if null return string
      if (typeof value === 'string' || value === null) {
        return 'text';
      }

      return typeof value === 'undefined' ? 'undefined' : _typeof(value);
    };

    /**
    * @ngdoc method
    * @name xos.uiComponents.XosFormHelpers#buildFormStructure
    * @methodOf xos.uiComponents.XosFormHelpers
    * @description
    * Return the type of the input
    * @param {object} modelField An object containing one property for each field of the model
    * @param {object} customField An object containing one property for each field custom field
    * @param {object} model The actual model on wich build the form structure (it is used to determine the type of the input)
    * @returns {object} An object describing the form structure in the form of:
    * ```
    * {
    *   'field-name': {
    *     label: 'Label',
    *     type: 'number', //typeof field
    *     validators: {}, // see xosForm for more details
    *     hint: 'A Custom hint for the field'
    *   }
    * }
    * ```
    **/

    this.buildFormStructure = function (modelField, customField, model) {

      modelField = angular.extend(modelField, customField);
      customField = customField || {};

      return _.reduce(Object.keys(modelField), function (form, f) {

        form[f] = {
          label: customField[f] && customField[f].label ? customField[f].label + ':' : LabelFormatter.format(f),
          type: customField[f] && customField[f].type ? customField[f].type : _this._getFieldFormat(model[f]),
          validators: customField[f] && customField[f].validators ? customField[f].validators : {},
          hint: customField[f] && customField[f].hint ? customField[f].hint : ''
        };

        if (customField[f] && customField[f].options) {
          form[f].options = customField[f].options;
        }
        if (form[f].type === 'date') {
          model[f] = new Date(model[f]);
        }

        if (form[f].type === 'number') {
          model[f] = parseInt(model[f], 10);
        }

        return form;
      }, {});
    };

    /**
    * @ngdoc method
    * @name xos.uiComponents.XosFormHelpers#parseModelField
    * @methodOf xos.uiComponents.XosFormHelpers
    * @description
    * Helpers for buildFormStructure, convert a list of model properties in an object used to build the form structure, eg:
    * ```
    * // input:
    * ['id', 'name'm 'mail']
    *
    * // output
    * {
    *   id: {},
    *   name: {},
    *   mail: {}
    * }
    * ```
    * @param {array} fields An array of fields representing the model properties
    * @returns {object} An object containing one property for each field of the model
    **/

    this.parseModelField = function (fields) {
      return _.reduce(fields, function (form, f) {
        form[f] = {};
        return form;
      }, {});
    };
  }]);
})();
//# sourceMappingURL=../../../maps/services/helpers/ui/form.helpers.js.map

'use strict';

(function () {
  'use strict';

  config.$inject = ["$httpProvider", "$interpolateProvider", "$resourceProvider"];
  angular.module('bugSnag', []).factory('$exceptionHandler', function () {
    return function (exception, cause) {
      if (window.Bugsnag) {
        Bugsnag.notifyException(exception, { diagnostics: { cause: cause } });
      } else {
        console.error(exception, cause, exception.stack);
      }
    };
  });

  /**
  * @ngdoc overview
  * @name xos.helpers
  * @description this is the module that group all the helpers service and components for XOS
  **/

  angular.module('xos.helpers', ['ngCookies', 'ngResource', 'ngAnimate', 'bugSnag', 'xos.uiComponents']).config(config)

  /**
  * @ngdoc service
  * @name xos.helpers._
  * @description Wrap [lodash](https://lodash.com/docs) in an Angular Service
  **/

  .factory('_', ["$window", function ($window) {
    return $window._;
  }]);

  function config($httpProvider, $interpolateProvider, $resourceProvider) {
    $httpProvider.interceptors.push('SetCSRFToken');

    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');

    // NOTE http://www.masnun.com/2013/09/18/django-rest-framework-angularjs-resource-trailing-slash-problem.html
    $resourceProvider.defaults.stripTrailingSlashes = false;
  }
})();
//# sourceMappingURL=maps/xosHelpers.module.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.vSG-Collection
  * @description Angular resource to fetch /api/service/vsg/
  **/
  .service('vSG-Collection', ["$resource", function ($resource) {
    return $resource('/api/service/vsg/');
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/vSG.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.vOLT-Collection
  * @description Angular resource to fetch /api/tenant/cord/volt/:volt_id/
  **/
  .service('vOLT-Collection', ["$resource", function ($resource) {
    return $resource('/api/tenant/cord/volt/:volt_id/', { volt_id: '@id' }, {
      update: { method: 'PUT' }
    });
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/vOLT.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Login
  * @description Angular resource to fetch /api/utility/login/
  **/
  .service('Login', ["$resource", function ($resource) {
    return $resource('/api/utility/login/');
  }])
  /**
  * @ngdoc service
  * @name xos.helpers.Logout
  * @description Angular resource to fetch /api/utility/logout/
  **/
  .service('Logout', ["$resource", function ($resource) {
    return $resource('/api/utility/logout/');
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/Utility.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Users
  * @description Angular resource to fetch /api/core/users/:id/
  **/
  .service('Users', ["$resource", function ($resource) {
    return $resource('/api/core/users/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/Users.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Truckroll
  * @description Angular resource to fetch /api/tenant/truckroll/:id/
  **/
  .service('Truckroll', ["$resource", function ($resource) {
    return $resource('/api/tenant/truckroll/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/Truckroll.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Tenant
  * @description Angular resource to fetch /api/core/tenant/:id/
  **/
  .service('Tenants', ["$resource", function ($resource) {
    return $resource('/api/core/tenants/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/Tenant.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Subscribers
  * @description Angular resource to fetch Subscribers
  **/
  .service('Subscribers', ["$resource", function ($resource) {
    return $resource('/api/tenant/cord/subscriber/:id/', { id: '@id' }, {
      update: { method: 'PUT' },
      /**
      * @ngdoc method
      * @name xos.helpers.Subscribers#View-a-Subscriber-Features-Detail
      * @methodOf xos.helpers.Subscribers
      * @description
      * View-a-Subscriber-Features-Detail
      **/
      'View-a-Subscriber-Features-Detail': {
        method: 'GET',
        isArray: false,
        url: '/api/tenant/cord/subscriber/:id/features/'
      },
      /**
      * @ngdoc method
      * @name xos.helpers.Subscribers#Read-Subscriber-uplink_speed
      * @methodOf xos.helpers.Subscribers
      * @description
      * Read-Subscriber-uplink_speed
      **/
      'Read-Subscriber-uplink_speed': {
        method: 'GET',
        isArray: false,
        url: '/api/tenant/cord/subscriber/:id/features/uplink_speed/'
      },
      /**
      * @ngdoc method
      * @name xos.helpers.Subscribers#Update-Subscriber-uplink_speed
      * @methodOf xos.helpers.Subscribers
      * @description
      * Update-Subscriber-uplink_speed
      **/
      'Update-Subscriber-uplink_speed': {
        method: 'PUT',
        isArray: false,
        url: '/api/tenant/cord/subscriber/:id/features/uplink_speed/'
      },
      /**
      * @ngdoc method
      * @name xos.helpers.Subscribers#Read-Subscriber-downlink_speed
      * @methodOf xos.helpers.Subscribers
      * @description
      * Read-Subscriber-downlink_speed
      **/
      'Read-Subscriber-downlink_speed': {
        method: 'GET',
        isArray: false,
        url: '/api/tenant/cord/subscriber/:id/features/downlink_speed/'
      },
      /**
      * @ngdoc method
      * @name xos.helpers.Subscribers#Update-Subscriber-downlink_speed
      * @methodOf xos.helpers.Subscribers
      * @description
      * Update-Subscriber-downlink_speed
      **/
      'Update-Subscriber-downlink_speed': {
        method: 'PUT',
        isArray: false,
        url: '/api/tenant/cord/subscriber/:id/features/downlink_speed/'
      },
      /**
      * @ngdoc method
      * @name xos.helpers.Subscribers#Read-Subscriber-cdn
      * @methodOf xos.helpers.Subscribers
      * @description
      * Read-Subscriber-cdn
      **/
      'Read-Subscriber-cdn': {
        method: 'GET',
        isArray: false,
        url: '/api/tenant/cord/subscriber/:id/features/cdn/'
      },
      /**
      * @ngdoc method
      * @name xos.helpers.Subscribers#Update-Subscriber-cdn
      * @methodOf xos.helpers.Subscribers
      * @description
      * Update-Subscriber-cdn
      **/
      'Update-Subscriber-cdn': {
        method: 'PUT',
        isArray: false,
        url: '/api/tenant/cord/subscriber/:id/features/cdn/'
      },
      /**
      * @ngdoc method
      * @name xos.helpers.Subscribers#Read-Subscriber-uverse
      * @methodOf xos.helpers.Subscribers
      * @description
      * Read-Subscriber-uverse
      **/
      'Read-Subscriber-uverse': {
        method: 'GET',
        isArray: false,
        url: '/api/tenant/cord/subscriber/:id/features/uverse/'
      },
      /**
      * @ngdoc method
      * @name xos.helpers.Subscribers#Update-Subscriber-uverse
      * @methodOf xos.helpers.Subscribers
      * @description
      * Update-Subscriber-uverse
      **/
      'Update-Subscriber-uverse': {
        method: 'PUT',
        isArray: false,
        url: '/api/tenant/cord/subscriber/:id/features/uverse/'
      },
      /**
      * @ngdoc method
      * @name xos.helpers.Subscribers#Read-Subscriber-status
      * @methodOf xos.helpers.Subscribers
      * @description
      * Read-Subscriber-status
      **/
      'Read-Subscriber-status': {
        method: 'GET',
        isArray: false,
        url: '/api/tenant/cord/subscriber/:id/features/status/'
      },
      /**
      * @ngdoc method
      * @name xos.helpers.Subscribers#Update-Subscriber-status
      * @methodOf xos.helpers.Subscribers
      * @description
      * Update-Subscriber-status
      **/
      'Update-Subscriber-status': {
        method: 'PUT',
        isArray: false,
        url: '/api/tenant/cord/subscriber/:id/features/status/'
      }
    });
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/Subscribers.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.SlicesPlus
  * @description Angular resource to fetch /api/utility/slicesplus/
  * This is a read-only API and only the `query` method is currently supported.
  **/
  .service('SlicesPlus', ["$http", "$q", function ($http, $q) {
    this.query = function (params) {
      var deferred = $q.defer();

      $http.get('/api/utility/slicesplus/', { params: params }).then(function (res) {
        deferred.resolve(res.data);
      }).catch(function (res) {
        deferred.reject(res.data);
      });

      return { $promise: deferred.promise };
    };

    this.get = function (id, params) {
      var deferred = $q.defer();

      $http.get('/api/utility/slicesplus/' + id, { params: params }).then(function (res) {
        deferred.resolve(res.data);
      }).catch(function (res) {
        deferred.reject(res.data);
      });
      return { $promise: deferred.promise };
    };
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/Slices_plus.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Slices
  * @description Angular resource to fetch /api/core/slices/:id/
  **/
  .service('Slices', ["$resource", function ($resource) {
    return $resource('/api/core/slices/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/Slices.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Sites
  * @description Angular resource to fetch /api/core/sites/:id/
  **/
  .service('Sites', ["$resource", function ($resource) {
    return $resource('/api/core/sites/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/Sites.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Services
  * @description Angular resource to fetch /api/core/services/:id/
  **/
  .service('Services', ["$resource", function ($resource) {
    return $resource('/api/core/services/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/Services.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.ONOS-Services-Collection
  * @description Angular resource to fetch /api/service/onos/
  **/
  .service('ONOS-Services-Collection', ["$resource", function ($resource) {
    return $resource('/api/service/onos/');
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/ONOS-Services.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.ONOS-App-Collection
  * @description Angular resource to fetch /api/tenant/onos/app/
  **/
  .service('ONOS-App-Collection', ["$resource", function ($resource) {
    return $resource('/api/tenant/onos/app/');
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/ONOS-Apps.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Nodes
  * @description Angular resource to fetch /api/core/nodes/:id/
  **/
  .service('Nodes', ["$resource", function ($resource) {
    return $resource('/api/core/nodes/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/Nodes.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Networks
  * @description Angular resource to fetch /api/core/networks/:id/
  **/
  .service('Networks', ["$resource", function ($resource) {
    return $resource('/api/core/networks/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/Networks.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Instances
  * @description Angular resource to fetch /api/core/instances/:id/
  **/
  .service('Instances', ["$resource", function ($resource) {
    return $resource('/api/core/instances/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/Instances.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Images
  * @description Angular resource to fetch /api/core/images/
  **/
  .service('Images', ["$resource", function ($resource) {
    return $resource('/api/core/images/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/Images.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Flavors
  * @description Angular resource to fetch /api/core/flavors/:id/
  **/
  .service('Flavors', ["$resource", function ($resource) {
    return $resource('/api/core/flavors/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/Flavors.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Example-Services-Collection
  * @description Angular resource to fetch /api/service/exampleservice/
  **/
  .service('Example-Services-Collection', ["$resource", function ($resource) {
    return $resource('/api/service/exampleservice/');
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/Example.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Deployments
  * @description Angular resource to fetch /api/core/deployments/:id/
  **/
  .service('Deployments', ["$resource", function ($resource) {
    return $resource('/api/core/deployments/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/Deployments.js.map

'use strict';

(function () {

  angular.module('xos.helpers')

  /**
  * @ngdoc service
  * @name xos.helpers.XosUserPrefs
  * @description
  * This service is used to store the user preferences in cookies, so that they survive to page changes.
  * The structure of the user preference is:
  * ```
  * {
  *   synchronizers: {
  *     notification: {
  *       'volt': boolean,
  *       'openstack': boolean,
  *       ...
  *     }
  *   }
  * }
  * ```
  **/

  .service('XosUserPrefs', ["$cookies", function ($cookies) {
    var _this = this;

    var userPrefs = $cookies.get('xosUserPrefs') ? JSON.parse($cookies.get('xosUserPrefs')) : {};

    /**
    * @ngdoc method
    * @name xos.helpers.XosUserPrefs#getAll
    * @methodOf xos.helpers.XosUserPrefs
    * @description
    * Return all the user preferences stored in cookies
    * @returns {object} The user preferences
    **/
    this.getAll = function () {
      userPrefs = $cookies.get('xosUserPrefs') ? JSON.parse($cookies.get('xosUserPrefs')) : {};
      return userPrefs;
    };

    /**
    * @ngdoc method
    * @name xos.helpers.XosUserPrefs#setAll
    * @methodOf xos.helpers.XosUserPrefs
    * @description
    * Override all user preferences
    * @param {object} prefs The user preferences
    **/
    this.setAll = function (prefs) {
      $cookies.put('xosUserPrefs', JSON.stringify(prefs));
    };

    /**
    * @ngdoc method
    * @name xos.helpers.XosUserPrefs#getSynchronizerNotificationStatus
    * @methodOf xos.helpers.XosUserPrefs
    * @description
    * Return the synchronizer notification status, if name is not provided return the status for all synchronizers
    * @param {string=} prefs The synchronizer name
    * @returns {object | string} The synchronizer status
    **/
    this.getSynchronizerNotificationStatus = function () {
      var name = arguments.length <= 0 || arguments[0] === undefined ? false : arguments[0];

      if (name) {
        return _this.getAll().synchronizers.notification[name];
      }
      return _this.getAll().synchronizers.notification;
    };

    /**
    * @ngdoc method
    * @name xos.helpers.XosUserPrefs#setSynchronizerNotificationStatus
    * @methodOf xos.helpers.XosUserPrefs
    * @description
    * Update the notification status for a single synchronizer
    * @param {string} name The synchronizer name
    * @param {boolean} value The notification status (true means that it has been sent)
    **/
    this.setSynchronizerNotificationStatus = function () {
      var name = arguments.length <= 0 || arguments[0] === undefined ? false : arguments[0];
      var value = arguments[1];

      if (!name) {
        throw new Error('[XosUserPrefs] When updating a synchronizer is mandatory to provide a name.');
      }

      var cookies = _this.getAll();

      if (!cookies.synchronizers) {
        cookies.synchronizers = {
          notification: {}
        };
      }

      cookies.synchronizers.notification[name] = value;
      _this.setAll(cookies);
    };
  }]);
})();
//# sourceMappingURL=../../maps/services/helpers/user-prefs.service.js.map

'use strict';

(function () {
  'use strict';

  /**
  * @ngdoc service
  * @name xos.helpers.ServiceGraph
  * @description This factory define a set of helper function to query the service tenancy graph
  **/

  angular.module('xos.helpers').service('GraphService', ["$q", "Tenants", "Services", function ($q, Tenants, Services) {
    var _this = this;

    this.loadCoarseData = function () {

      var services = void 0;

      var deferred = $q.defer();

      Services.query().$promise.then(function (res) {
        services = res;
        return Tenants.query({ kind: 'coarse' }).$promise;
      }).then(function (tenants) {
        deferred.resolve({
          tenants: tenants,
          services: services
        });
      });

      return deferred.promise;
    };

    this.getCoarseGraph = function () {
      _this.loadCoarseData().then(function (res) {
        console.log(res);
      });
      return 'ciao';
    };
  }]);
})();
//# sourceMappingURL=../maps/services/service_graph.service.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers').factory('Notification', function () {
    return window.Notification;
  })
  /**
  * @ngdoc service
  * @name xos.helpers.xosNotification
  * @description This factory define a set of helper function to trigger desktop notification
  **/
  .service('xosNotification', ["$q", "$log", "Notification", function ($q, $log, Notification) {
    var _this = this;

    this.checkPermission = function () {
      var deferred = $q.defer();
      Notification.requestPermission().then(function (permission) {
        if (permission === 'granted') {
          deferred.resolve(permission);
        } else {
          deferred.reject(permission);
        }
      });
      return deferred.promise;
    };

    this.sendNotification = function (title, options) {
      var notification = new Notification(title, options);
      notification.onerror = function (err) {
        $log.error(err);
      };
    };

    /**
    * @ngdoc method
    * @name xos.helpers.xosNotification#notify
    * @methodOf xos.helpers.xosNotification
    * @description
    * This method will check for user permission and if granted will send a browser notification.
    * @param {string} title The notification title
    * @param {object} options The notification options: `{icon: 'url', body: 'Notification body'}`
    **/

    this.notify = function (title, options) {
      if (!('Notification' in window)) {
        $log.info('This browser does not support desktop notification');
      } else if (Notification.permission !== 'granted') {
        _this.checkPermission().then(function () {
          return _this.sendNotification(title, options);
        });
      } else if (Notification.permission === 'granted') {
        _this.sendNotification(title, options);
      }
    };
  }]);
})();
//# sourceMappingURL=../maps/services/notification.service.js.map

'use strict';

(function () {
  'use strict';

  /**
  * @ngdoc service
  * @name xos.helpers.NoHyperlinks
  * @description This factory is automatically loaded trough xos.helpers and will add an $http interceptor that will add ?no_hyperlinks=1 to your api request, that is required by django
  **/

  angular.module('xos.helpers').factory('NoHyperlinks', noHyperlinks);

  function noHyperlinks() {
    return {
      request: function request(_request) {
        if (_request.url.indexOf('.html') === -1) {
          _request.url += '?no_hyperlinks=1';
        }
        return _request;
      }
    };
  }
})();
//# sourceMappingURL=../maps/services/noHyperlinks.interceptor.js.map

'use strict';

// TODO write tests for log

angular.module('xos.helpers').config(['$provide', function ($provide) {
  // Use the `decorator` solution to substitute or attach behaviors to
  // original service instance; @see angular-mocks for more examples....

  $provide.decorator('$log', ['$delegate', function ($delegate) {

    var isLogEnabled = function isLogEnabled() {
      return window.location.href.indexOf('debug=true') >= 0;
    };
    // Save the original $log.debug()
    var logFn = $delegate.log;
    var infoFn = $delegate.info;
    var warnFn = $delegate.warn;
    var errorFn = $delegate.error;
    var debugFn = $delegate.debug;

    // create the replacement function
    var replacement = function replacement(fn) {
      return function () {
        // console.log(`Is Log Enabled: ${isLogEnabled()}`)
        if (!isLogEnabled()) {
          // console.log('logging is disabled');
          return;
        }
        var args = [].slice.call(arguments);
        var now = new Date();

        // Prepend timestamp
        args[0] = '[' + now.getHours() + ':' + now.getMinutes() + ':' + now.getSeconds() + '] ' + args[0];

        // HACK awfull fix for angular mock implementation whithin jasmine test failing issue
        if (typeof $delegate.reset === 'function' && !($delegate.debug.logs instanceof Array)) {
          // if we are within the mock and did not reset yet, we call it to avoid issue
          // console.log('mock log impl fix to avoid logs array not existing...');
          $delegate.reset();
        }

        // Call the original with the output prepended with formatted timestamp
        fn.apply(null, args);
      };
    };

    $delegate.info = replacement(infoFn);
    $delegate.log = replacement(logFn);
    $delegate.warn = replacement(warnFn);
    $delegate.error = replacement(errorFn);
    $delegate.debug = replacement(debugFn);

    return $delegate;
  }]);
}]);
//# sourceMappingURL=../maps/services/log.decorator.js.map

'use strict';

(function () {
  'use strict';

  /**
  * @ngdoc service
  * @name xos.helpers.SetCSRFToken
  * @description This factory is automatically loaded trough xos.helpers and will add an $http interceptor that will the CSRF-Token to your request headers
  **/

  setCSRFToken.$inject = ["$cookies"];
  angular.module('xos.helpers').factory('SetCSRFToken', setCSRFToken);

  function setCSRFToken($cookies) {
    return {
      request: function request(_request) {
        if (_request.method !== 'GET') {
          _request.headers['X-CSRFToken'] = $cookies.get('xoscsrftoken');
        }
        return _request;
      }
    };
  }
})();
//# sourceMappingURL=../maps/services/csrfToken.interceptor.js.map
