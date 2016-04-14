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

  angular.module('xos.uiComponents.table', []).directive('xosTable', function () {
    return {
      restrict: 'E',
      scope: {
        data: '=',
        columns: '='
      },
      template: '\n          <!--<pre>{{vm.data | json}}</pre>-->\n          <table class="table table-striped" ng-show="vm.data.length > 0">\n            <thead>\n              <tr>\n                <th ng-repeat="col in vm.columns">{{col}}</th>\n              </tr>\n            </thead>\n            <tbody>\n              <tr ng-repeat="item in vm.data">\n                <td ng-repeat="col in vm.columns">{{item[col]}}</td>\n              </tr>\n            </tbody>\n          </table>\n        ',
      bindToController: true,
      controllerAs: 'vm',
      controller: function controller() {
        console.log(this.data, this.columns);
        console.log('Bella dello zio, RELOAD');
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
