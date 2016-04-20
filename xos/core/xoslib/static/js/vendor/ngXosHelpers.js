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

  angular.module('xos.helpers', ['ngCookies', 'ngResource', 'bugSnag', 'xos.uiComponents']).config(config).factory('_', ["$window", function ($window) {
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
    return $resource('/api/tenant/cord/volt/:volt_id/', { volt_id: '@id' });
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/vOLT.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Users
  * @description Angular resource to fetch /api/core/users/
  **/
  .service('Users', ["$resource", function ($resource) {
    return $resource('/api/core/users/');
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/Users.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Truckroll-Collection
  * @description Angular resource to fetch /api/tenant/truckroll/:truckroll_id/
  **/
  .service('Truckroll-Collection', ["$resource", function ($resource) {
    return $resource('/api/tenant/truckroll/:truckroll_id/', { truckroll_id: '@id' });
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/Truckroll.js.map

'use strict';

(function () {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Subscribers
  * @description Angular resource to fetch /api/tenant/cord/subscriber/:subscriber_id/
  **/
  .service('Subscribers', ["$resource", function ($resource) {
    return $resource('/api/tenant/cord/subscriber/:subscriber_id/', { subscriber_id: '@id' });
  }])
  /**
  * @ngdoc service
  * @name xos.helpers.Subscriber-features
  * @description Angular resource to fetch /api/tenant/cord/subscriber/:subscriber_id/features/
  **/
  .service('Subscriber-features', ["$resource", function ($resource) {
    return $resource('/api/tenant/cord/subscriber/:subscriber_id/features/', { subscriber_id: '@id' });
  }])
  /**
  * @ngdoc service
  * @name xos.helpers.Subscriber-features-uplink_speed
  * @description Angular resource to fetch /api/tenant/cord/subscriber/:subscriber_id/features/uplink_speed/
  **/
  .service('Subscriber-features-uplink_speed', ["$resource", function ($resource) {
    return $resource('/api/tenant/cord/subscriber/:subscriber_id/features/uplink_speed/', { subscriber_id: '@id' });
  }])
  /**
  * @ngdoc service
  * @name xos.helpers.Subscriber-features-downlink_speed
  * @description Angular resource to fetch /api/tenant/cord/subscriber/:subscriber_id/features/downlink_speed/
  **/
  .service('Subscriber-features-downlink_speed', ["$resource", function ($resource) {
    return $resource('/api/tenant/cord/subscriber/:subscriber_id/features/downlink_speed/', { subscriber_id: '@id' });
  }])
  /**
  * @ngdoc service
  * @name xos.helpers.Subscriber-features-cdn
  * @description Angular resource to fetch /api/tenant/cord/subscriber/:subscriber_id/features/cdn/
  **/
  .service('Subscriber-features-cdn', ["$resource", function ($resource) {
    return $resource('/api/tenant/cord/subscriber/:subscriber_id/features/cdn/', { subscriber_id: '@id' });
  }])
  /**
  * @ngdoc service
  * @name xos.helpers.Subscriber-features-uverse
  * @description Angular resource to fetch /api/tenant/cord/subscriber/:subscriber_id/features/uverse/
  **/
  .service('Subscriber-features-uverse', ["$resource", function ($resource) {
    return $resource('/api/tenant/cord/subscriber/:subscriber_id/features/uverse/', { subscriber_id: '@id' });
  }])
  /**
  * @ngdoc service
  * @name xos.helpers.Subscriber-features-status
  * @description Angular resource to fetch /api/tenant/cord/subscriber/:subscriber_id/features/status/
  **/
  .service('Subscriber-features-status', ["$resource", function ($resource) {
    return $resource('/api/tenant/cord/subscriber/:subscriber_id/features/status/', { subscriber_id: '@id' });
  }]);
})();
//# sourceMappingURL=../../maps/services/rest/Subscribers.js.map

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
  * @description A collection of UI components useful for Dashboard development
  **/

  angular.module('xos.uiComponents', []);
})();
//# sourceMappingURL=../maps/ui_components/ui-components.module.js.map

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
  <example module="sampleTable2">
  <file name="index.html">
    <div ng-controller="SampleCtrl2 as vm">
      <xos-table data="vm.data" config="vm.config"></xos-table>
    </div>
  </file>
  <file name="script.js">
    angular.module('sampleTable2', ['xos.uiComponents'])
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

  .directive('xosTable', function () {
    return {
      restrict: 'E',
      scope: {
        data: '=',
        config: '='
      },
      template: '\n          <div ng-show="vm.data.length > 0">\n            <div class="row" ng-if="vm.config.filter == \'fulltext\'">\n              <div class="col-xs-12">\n                <input\n                  class="form-control"\n                  placeholder="Type to search.."\n                  type="text"\n                  ng-model="vm.query"/>\n              </div>\n            </div>\n            <table ng-class="vm.classes" ng-show="vm.data.length > 0">\n              <thead>\n                <tr>\n                  <th ng-repeat="col in vm.columns">\n                    {{col.label}}\n                    <span ng-if="vm.config.order">\n                      <a href="" ng-click="vm.orderBy = col.prop; vm.reverse = false">\n                        <i class="glyphicon glyphicon-chevron-up"></i>\n                      </a>\n                      <a href="" ng-click="vm.orderBy = col.prop; vm.reverse = true">\n                        <i class="glyphicon glyphicon-chevron-down"></i>\n                      </a>\n                    </span>\n                  </th>\n                  <th ng-if="vm.config.actions">Actions</th>\n                </tr>\n              </thead>\n              <tbody ng-if="vm.config.filter == \'field\'">\n                <tr>\n                  <td ng-repeat="col in vm.columns">\n                    <input\n                      class="form-control"\n                      placeholder="Type to search by {{col.label}}"\n                      type="text"\n                      ng-model="vm.query[col.prop]"/>\n                  </td>\n                  <td ng-if="vm.config.actions"></td>\n                </tr>\n              </tbody>\n              <tbody>\n                <tr ng-repeat="item in vm.data | filter:vm.query | orderBy:vm.orderBy:vm.reverse | pagination:vm.currentPage * vm.config.pagination.pageSize | limitTo: (vm.config.pagination.pageSize || vm.data.length) track by $index">\n                  <td ng-repeat="col in vm.columns">{{item[col.prop]}}</td>\n                  <td ng-if="vm.config.actions">\n                    <a href=""\n                      ng-repeat="action in vm.config.actions"\n                      ng-click="action.cb(item)"\n                      title="{{action.label}}">\n                      <i\n                        class="glyphicon glyphicon-{{action.icon}}"\n                        style="color: {{action.color}};"></i>\n                    </a>\n                  </td>\n                </tr>\n              </tbody>\n            </table>\n            <xos-pagination\n              ng-if="vm.config.pagination"\n              page-size="vm.config.pagination.pageSize"\n              total-elements="vm.data.length"\n              change="vm.goToPage">\n              </xos-pagination>\n          </div>\n          <div ng-show="vm.data.length == 0 || !vm.data">\n             <xos-alert config="{type: \'info\'}">\n              No data to show.\n            </xos-alert>\n          </div>\n        ',
      bindToController: true,
      controllerAs: 'vm',
      controller: function controller() {
        var _this = this;

        if (!this.config) {
          throw new Error('[xosTable] Please provide a configuration via the "config" attribute');
        }

        if (!this.config.columns) {
          throw new Error('[xosTable] Please provide a columns list in the configuration');
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
      }
    };
  });
})();
//# sourceMappingURL=../../maps/ui_components/dumbComponents/table.component.js.map

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
//# sourceMappingURL=../../maps/ui_components/dumbComponents/pagination.component.js.map

'use strict';

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol ? "symbol" : typeof obj; };

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
    * @description The xos-form directive
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
    *   ]
    * }
    * ```
    * @element ANY
    * @scope
    * @example
  <example module="sampleAlert1">
    <file name="index.html">
      <div ng-controller="SampleCtrl1 as vm">
        
      </div>
    </file>
    <file name="script.js">
      angular.module('sampleAlert1', ['xos.uiComponents'])
      .controller('SampleCtrl1', function(){
        this.config1 = {
          exclude: ['password', 'last_login']
        };
      });
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
      template: '\n        <ng-form name="vm.config.formName || \'form\'">\n          <div class="form-group" ng-repeat="field in vm.formField">\n            <label>{{vm.formatLabel(field.label)}}</label>\n            <input type="text" name="" class="form-control" ng-model="vm.ngModel[field]"/>\n          </div>\n          <div class="form-group" ng-if="vm.config.actions">\n            <button href=""\n              ng-repeat="action in vm.config.actions"\n              ng-click="action.cb(vm.ngModel)"\n              class="btn btn-{{action.class}}"\n              title="{{action.label}}">\n              <i class="glyphicon glyphicon-{{action.icon}}"></i>\n              {{action.label}}\n            </button>\n          </div>\n        </ng-form>\n      ',
      bindToController: true,
      controllerAs: 'vm',
      controller: ["$scope", "$log", "_", "LabelFormatter", "XosFormHelpers", function controller($scope, $log, _, LabelFormatter, XosFormHelpers) {
        var _this = this;

        if (!this.config) {
          throw new Error('[xosForm] Please provide a configuration via the "config" attribute');
        }

        if (!this.config.actions) {
          throw new Error('[xosForm] Please provide an action list in the configuration');
        }

        this.formatLabel = LabelFormatter.format;

        this.excludedField = ['id', 'validators', 'created', 'updated', 'deleted', 'backend_status'];
        if (this.config && this.config.exclude) {
          this.excludedField = this.excludedField.concat(this.config.exclude);
        }

        this.formField = [];
        $scope.$watch(function () {
          return _this.ngModel;
        }, function (model) {
          if (!model) {
            return;
          }
          _this.formField = XosFormHelpers.buildFormStructure(_.difference(Object.keys(model), _this.excludedField));
        });
      }]
    };
  }).service('XosFormHelpers', ["_", "LabelFormatter", function (_, LabelFormatter) {
    var _this2 = this;

    this._getFieldFormat = function (value) {

      // check if is date
      if (_.isDate(value)) {
        return 'date';
      }

      // check if is boolean
      // isNaN(false) = false, false is a number (0), true is a number (1)
      if (typeof value === 'boolean') {
        return 'boolean';
      }

      // check if a string is a number
      if (!isNaN(value)) {
        return 'number';
      }

      return typeof value === 'undefined' ? 'undefined' : _typeof(value);
    };

    this.buildFormStructure = function (modelField, customField, model) {
      return _.reduce(Object.keys(modelField), function (form, f) {
        form[f] = {
          label: customField[f] && customField[f].label ? customField[f].label + ':' : LabelFormatter.format(f),
          type: customField[f] && customField[f].type ? customField[f].type : _this2._getFieldFormat(model[f]),
          validators: {}
        };
        return form;
      }, {});
    };

    this.parseModelField = function (fields) {
      return _.reduce(fields, function (form, f) {
        form[f] = {};
        return form;
      }, {});
    };
  }]);
})();
//# sourceMappingURL=../../maps/ui_components/dumbComponents/form.component.js.map

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
   <example module="sampleAlert2">
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
      angular.module('sampleAlert2', ['xos.uiComponents'])
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
      template: '\n        <div class="alert alert-{{vm.config.type}}" ng-show="vm.show">\n          <button type="button" class="close" ng-if="vm.config.closeBtn" ng-click="vm.dismiss()">\n            <span aria-hidden="true">&times;</span>\n          </button>\n          <p ng-transclude></p>\n        </div>\n      ',
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
//# sourceMappingURL=../../maps/ui_components/dumbComponents/alert.component.js.map

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
    var debugFn = $delegate.info;

    // create the replacement function
    var replacement = function replacement(fn) {
      return function () {
        if (!isLogEnabled()) {
          console.log('logging is disabled');
          return;
        }
        var args = [].slice.call(arguments);
        var now = new Date();

        // Prepend timestamp
        args[0] = '[' + now.getHours() + ':' + now.getMinutes() + ':' + now.getSeconds() + '] ' + args[0];

        // Call the original with the output prepended with formatted timestamp
        fn.apply(null, args);
      };
    };

    $delegate.info = replacement(debugFn);

    return $delegate;
  }]);
}]);
//# sourceMappingURL=../maps/services/log.decorator.js.map

'use strict';

(function () {
  'use strict';

  /**
  * @ngdoc service
  * @name xos.helpers.LabelFormatter
  * @description This factory define a set of helper function to format label started from an object property
  **/

  angular.module('xos.helpers').factory('LabelFormatter', labelFormatter);

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

      return _capitalize(string).replace(/\s\s+/g, ' ') + ':';
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
//# sourceMappingURL=../maps/services/label_formatter.service.js.map

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
