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
      ],
      filter: 'field', // can be by `field` or `fulltext`
      order: true // whether to show ordering arrows
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
   **/

  .directive('xosTable', function () {
    return {
      restrict: 'E',
      scope: {
        data: '=',
        config: '='
      },
      template: '\n          <!-- <pre>{{vm.data | json}}</pre> -->\n          <div class="row" ng-if="vm.config.filter == \'fulltext\'">\n            <div class="col-xs-12">\n              <input\n                class="form-control"\n                placeholder="Type to search.."\n                type="text"\n                ng-model="vm.query"/>\n            </div>\n          </div>\n          <table ng-class="vm.classes" ng-show="vm.data.length > 0">\n            <thead>\n              <tr>\n                <th ng-repeat="col in vm.columns">\n                  {{col.label}}\n                  <span ng-if="vm.config.order">\n                    <a href="" ng-click="vm.orderBy = col.prop; vm.reverse = false">\n                      <i class="glyphicon glyphicon-chevron-up"></i>\n                    </a>\n                    <a href="" ng-click="vm.orderBy = col.prop; vm.reverse = true">\n                      <i class="glyphicon glyphicon-chevron-down"></i>\n                    </a>\n                  </span>\n                </th>\n                <th ng-if="vm.config.actions">Actions</th>\n              </tr>\n            </thead>\n            <tbody ng-if="vm.config.filter == \'field\'">\n              <tr>\n                <td ng-repeat="col in vm.columns">\n                  <input\n                    class="form-control"\n                    placeholder="Type to search by {{col.label}}"\n                    type="text"\n                    ng-model="vm.query[col.prop]"/>\n                </td>\n                <td ng-if="vm.config.actions"></td>\n              </tr>\n            </tbody>\n            <tbody>\n              <tr ng-repeat="item in vm.data | filter:vm.query | orderBy:vm.orderBy:vm.reverse">\n                <td ng-repeat="col in vm.columns">{{item[col.prop]}}</td>\n                <td ng-if="vm.config.actions">\n                  <a href=""\n                    ng-repeat="action in vm.config.actions"\n                    ng-click="action.cb(item)"\n                    title="{{action.label}}">\n                    <i\n                      class="glyphicon glyphicon-{{action.icon}}"\n                      style="color: {{action.color}};"></i>\n                  </a>\n                </td>\n              </tr>\n            </tbody>\n          </table>\n        ',
      bindToController: true,
      controllerAs: 'vm',
      controller: function controller() {

        if (!this.config) {
          throw new Error('[xosTable] Please provide a configuration via the "config" attribute');
        }

        if (!this.config.columns) {
          throw new Error('[xosTable] Please provide a columns list in the configuration');
        }

        this.columns = this.config.columns;
        this.classes = this.config.classes || 'table table-striped table-bordered';

        if (this.config.actions) {}
      }
    };
  });
})();
//# sourceMappingURL=../../maps/ui_components/table/table.component.js.map

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

  angular.module('xos.helpers', ['ngCookies', 'ngResource', 'bugSnag', 'xos.uiComponents']).config(config);

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
  * @requires xos.uiComponents.table
  **/

  angular.module('xos.uiComponents', ['xos.uiComponents.table']);
})();
//# sourceMappingURL=../maps/ui_components/ui-components.module.js.map

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
