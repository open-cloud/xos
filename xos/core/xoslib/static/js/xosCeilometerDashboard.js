'use strict';

angular.module('xos.ceilometerDashboard', ['ngResource', 'ngCookies', 'ngLodash', 'ui.router', 'xos.helpers', 'ngAnimate', 'chart.js', 'ui.bootstrap.accordion']).config(["$stateProvider", "$urlRouterProvider", function ($stateProvider, $urlRouterProvider) {
  $stateProvider.state('ceilometerDashboard', {
    url: '/',
    template: '<ceilometer-dashboard></ceilometer-dashboard>'
  }).state('samples', {
    url: '/:name/:tenant/samples',
    template: '<ceilometer-samples></ceilometer-samples>'
  });
  $urlRouterProvider.otherwise('/');
}]).config(["$httpProvider", function ($httpProvider) {
  $httpProvider.interceptors.push('NoHyperlinks');
}]).run(["$rootScope", function ($rootScope) {
  $rootScope.stateName = 'ceilometerDashboard';
  $rootScope.$on('$stateChangeStart', function (event, toState) {
    $rootScope.stateName = toState.name;
  });
}]);
angular.module("xos.ceilometerDashboard").run(["$templateCache", function($templateCache) {$templateCache.put("templates/accordion-group.html","<div class=\"panel {{panelClass || \'panel-default\'}}\">\n  <div class=\"panel-heading\" ng-keypress=\"toggleOpen($event)\">\n    <h5>\n      <a href tabindex=\"0\" class=\"accordion-toggle\" ng-click=\"toggleOpen()\" uib-accordion-transclude=\"heading\"><span ng-class=\"{\'text-muted\': isDisabled}\">{{heading}}</span></a>\n    </h5>\n  </div>\n  <div class=\"panel-collapse collapse\" uib-collapse=\"!isOpen\">\n	  <div class=\"panel-body\" ng-transclude></div>\n  </div>\n</div>\n");
$templateCache.put("templates/accordion.html","<div class=\"panel-group\" ng-transclude></div>");
$templateCache.put("templates/ceilometer-dashboard.tpl.html","<div class=\"row\">\n  <div class=\"col-sm-10\">\n    <h3>XOS Monitoring Statistics</h3>\n  </div>\n  <div class=\"col-xs-2 text-right\">\n    <a href=\"\" class=\"btn btn-default\" \n      ng-show=\"vm.selectedSlice && !vm.showStats\"\n      ng-click=\"vm.showStats = true\">\n      <i class=\"glyphicon glyphicon-transfer\"></i>\n    </a>\n    <a href=\"\" class=\"btn btn-default\" \n      ng-show=\"vm.selectedSlice && vm.showStats\"\n      ng-click=\"vm.showStats = false\">\n      <i class=\"glyphicon glyphicon-transfer\"></i>\n    </a>\n  </div>\n</div>\n\n<div class=\"row\" ng-show=\"vm.loader\">\n  <div class=\"col-xs-12\">\n    <div class=\"loader\">Loading</div>\n  </div>\n</div>\n\n<section ng-hide=\"vm.loader\" ng-class=\"{animate: !vm.loader}\">\n  <div class=\"row\">\n    <div class=\"col-sm-3 service-list\">\n        <h4>XOS Service: </h4>\n        <uib-accordion close-others=\"true\" template-url=\"templates/accordion.html\">\n          <uib-accordion-group\n            ng-repeat=\"service in vm.services | orderBy:\'-service\'\"\n            template-url=\"templates/accordion-group.html\"\n            is-open=\"vm.accordion.open[service.service]\"\n            heading=\"{{service.service}}\">\n            <h5>Slices:</h5>\n            <a ng-repeat=\"slice in service.slices\" \n              ng-class=\"{active: slice.slice === vm.selectedSlice}\"\n              ng-click=\"vm.loadSliceMeter(slice, service.service)\"\n              href=\"#\" class=\"list-group-item\" >\n              {{slice.slice}} <i class=\"glyphicon glyphicon-chevron-right pull-right\"></i>\n            </a>\n          </uib-accordion-group>\n        </uib-accordion>\n    </div>\n    <section class=\"side-container col-sm-9\">\n      <div class=\"row\">\n        <!-- STATS -->\n        <article ng-hide=\"!vm.showStats\" class=\"stats animate-slide-left\">\n          <div class=\"col-xs-12\">\n            <div class=\"list-group\">\n              <div class=\"list-group-item\">\n                <h4>Stats</h4>\n              </div>\n              <div class=\"list-group-item\">\n                <ceilometer-stats ng-if=\"vm.selectedSlice\" name=\"vm.selectedSlice\" tenant=\"vm.selectedTenant\"></ceilometer-stats>\n              </div>\n            </div>\n          </div>\n        </article>\n        <!-- METERS -->\n        <article ng-hide=\"vm.showStats\" class=\"meters animate-slide-left\">\n          <div class=\"alert alert-danger\" ng-show=\"vm.ceilometerError\">\n            {{vm.ceilometerError}}\n          </div>\n          <div class=\"col-sm-4 animate-slide-left\" ng-hide=\"!vm.selectedSlice\">\n            <div class=\"list-group\">\n              <div class=\"list-group-item\">\n                <h4>Resources</h4>\n              </div>\n              <a href=\"#\" \n                ng-click=\"vm.selectMeters(meters, resource)\" \n                class=\"list-group-item\" \n                ng-repeat=\"(resource, meters) in vm.selectedResources\" \n                ng-class=\"{active: resource === vm.selectedResource}\">\n                {{resource}} <i class=\"glyphicon glyphicon-chevron-right pull-right\"></i>\n              </a>\n            </div>\n          </div>\n          <div class=\"col-sm-8 animate-slide-left\" ng-hide=\"!vm.selectedMeters\">\n            <div class=\"list-group\">\n              <div class=\"list-group-item\">\n                <h4>Meters</h4>\n              </div>\n              <div class=\"list-group-item\">\n                <div class=\"row\">\n                  <div class=\"col-xs-6\">\n                    <label>Name:</label>\n                  </div>\n                  <div class=\"col-xs-3\">\n                    <label>Unit:</label>\n                  </div>\n                  <div class=\"col-xs-3\"></div>\n                </div>\n                <div class=\"row\" ng-repeat=\"meter in vm.selectedMeters\" style=\"margin-bottom: 10px;\">\n                  <div class=\"col-xs-6\">\n                    {{meter.name}}\n                  </div>\n                  <div class=\"col-xs-3\">\n                    {{meter.unit}}\n                  </div>\n                  <div class=\"col-xs-3\">\n                    <!-- tenant: meter.resource_id -->\n                    <a ui-sref=\"samples({name: meter.name, tenant: meter.resource_id})\" class=\"btn btn-primary\">\n                      <i class=\"glyphicon glyphicon-search\"></i>\n                    </a>\n                  </div>\n                </div>\n              </div>\n            </div>\n          </div>\n        </article>\n      </div>\n    </section>\n  </div>\n</section>\n<section ng-if=\"!vm.loader && vm.error\">\n  <div class=\"alert alert-danger\">\n    {{vm.error}}\n  </div>\n</section>\n");
$templateCache.put("templates/ceilometer-samples.tpl.html","<!-- <pre>{{ vm | json}}</pre> -->\n\n<div class=\"row\">\n  <div class=\"col-xs-10\">\n    <h1>{{vm.name | uppercase}}</h1>\n  </div>\n  <div class=\"col-xs-2\">\n    <a ui-sref=\"ceilometerDashboard\" class=\"btn btn-primary pull-right\">\n      <i class=\"glyphicon glyphicon-arrow-left\"></i> Back to list\n    </a>\n  </div>\n</div>\n<div class=\"row\" ng-show=\"vm.loader\">\n  <div class=\"col-xs-12\">\n    <div class=\"loader\">Loading</div>\n  </div>\n</div>\n<section ng-if=\"!vm.loader && !vm.error\">\n  <div class=\"row\">\n    <form class=\"form-inline col-xs-8\" ng-submit=\"vm.addMeterToChart(vm.addMeterValue)\">\n      <select ng-model=\"vm.addMeterValue\" class=\"form-control\" ng-options=\"resource.id as resource.name for resource in vm.sampleLabels\"></select>\n      <button class=\"btn btn-success\"> \n        <i class=\"glyphicon glyphicon-plus\"></i> Add\n      </button>\n    </form>\n    <div class=\"col-xs-4 text-right\">\n      <a ng-click=\"vm.chartType = \'line\'\" class=\"btn\" ng-class=\"{\'btn-default\': vm.chartType != \'bar\', \'btn-primary\': vm.chartType == \'line\'}\">Lines</a>\n      <a ng-click=\"vm.chartType = \'bar\'\" class=\"btn\" ng-class=\"{\'btn-default\': vm.chartType != \'line\', \'btn-primary\': vm.chartType == \'bar\'}\">Bars</a>\n    </div>\n  </div>\n  <div class=\"row\" ng-if=\"!vm.loader\">\n    <div class=\"col-xs-12\">\n      <canvas ng-if=\"vm.chartType === \'line\'\" id=\"line\" class=\"chart chart-line\" chart-data=\"vm.chart.data\" chart-options=\"{datasetFill: false}\"\n        chart-labels=\"vm.chart.labels\" chart-legend=\"false\" chart-series=\"vm.chart.series\">\n      </canvas>\n      <canvas ng-if=\"vm.chartType === \'bar\'\" id=\"bar\" class=\"chart chart-bar\" chart-data=\"vm.chart.data\"\n        chart-labels=\"vm.chart.labels\" chart-legend=\"false\" chart-series=\"vm.chart.series\">\n      </canvas>\n      <!-- <pre>{{vm.chartMeters | json}}</pre> -->\n    </div>\n  </div>\n  <div class=\"row\" ng-if=\"!vm.loader\">\n    <div class=\"col-xs-12\">\n      <a ng-click=\"vm.removeFromChart(meter)\" class=\"btn btn-chart\" ng-style=\"{\'background-color\': vm.chartColors[$index]}\" ng-repeat=\"meter in vm.chartMeters\">\n        {{meter.resource_name || meter.resource_id}}\n      </a>\n    </div>\n  </div>\n</section>\n<section ng-if=\"!vm.loader && vm.error\">\n  <div class=\"alert alert-danger\">\n    {{vm.error}}\n  </div>\n</section>");
$templateCache.put("templates/ceilometer-stats.tpl.html","<div ng-show=\"vm.loader\" class=\"loader\">Loading</div>\n\n<section ng-if=\"!vm.loader && !vm.error\">\n\n  <div class=\"alert alert-danger\" ng-if=\"vm.stats.length == 0\">\n    No result\n  </div>  \n\n  <table class=\"table\" ng-if=\"vm.stats.length > 0\">\n    <tr>\n      <th>\n        <a ng-click=\"(order == \'category\') ? order = \'-category\' : order = \'category\'\">Type:</a>\n      </th>\n      <th>\n        <a ng-click=\"(order == \'resource_name\') ? order = \'-resource_name\' : order = \'resource_name\'\">Resource:</a>\n      </th>\n      <th>\n        <a ng-click=\"(order == \'meter\') ? order = \'-meter\' : order = \'meter\'\">Meter:</a>\n      </th>\n      <th>\n        Unit:\n      </th>\n      <th>\n        Value:\n      </th>\n    </tr>\n    <!-- <tr>\n      <td>\n        <input type=\"text\" ng-model=\"query.category\">\n      </td>\n      <td>\n        <input type=\"text\" ng-model=\"query.resource_name\">\n      </td>\n      <td>\n        <input type=\"text\" ng-model=\"query.meter\">\n      </td>\n      <td>\n        <input type=\"text\" ng-model=\"query.unit\">\n      </td>\n      <td>\n        <input type=\"text\" ng-model=\"query.value\">\n      </td>\n    </tr> -->\n    <tr ng-repeat=\"item in vm.stats | orderBy:order\">\n      <td>{{item.category}}</td>\n      <td>{{item.resource_name}}</td>\n      <td>{{item.meter}}</td>\n      <td>{{item.unit}}</td>\n      <td>{{item.value}}</td>\n    </tr>\n  </table>\n</section>\n\n<section ng-if=\"!vm.loader && vm.error\">\n  <div class=\"alert alert-danger\">\n    {{vm.error}}\n  </div>\n</section>\n");}]);
angular.module('xos.ceilometerDashboard').run(["$location", function($location){$location.path('/')}]);
angular.element(document).ready(function() {angular.bootstrap(angular.element('#xosCeilometerDashboard'), ['xos.ceilometerDashboard']);});
/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 3/21/16.
 */

'use strict';

(function () {
  'use strict';

  angular.module('xos.ceilometerDashboard').directive('ceilometerStats', function () {
    return {
      restrict: 'E',
      scope: {
        name: '=name',
        tenant: '=tenant'
      },
      bindToController: true,
      controllerAs: 'vm',
      templateUrl: 'templates/ceilometer-stats.tpl.html',
      controller: ["$scope", "Ceilometer", function controller($scope, Ceilometer) {
        var _this = this;

        this.getStats = function (tenant) {
          _this.loader = true;
          Ceilometer.getStats({ tenant: tenant }).then(function (res) {
            res.map(function (m) {
              m.resource_name = m.resource_name.replace('mysite_onos_vbng', 'ONOS_FABRIC');
              m.resource_name = m.resource_name.replace('mysite_onos_volt', 'ONOS_CORD');
              m.resource_name = m.resource_name.replace('mysite_vbng', 'mysite_vRouter');
              return m;
            });
            _this.stats = res;
          })['catch'](function (err) {
            _this.error = err.data;
          })['finally'](function () {
            _this.loader = false;
          });
        };

        $scope.$watch(function () {
          return _this.name;
        }, function (val) {
          if (val) {
            _this.getStats(_this.tenant);
          }
        });
      }]
    };
  });
})();
/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 3/21/16.
 */

'use strict';

(function () {
  'use strict';

  angular.module('xos.ceilometerDashboard').directive('ceilometerSamples', ["lodash", "$stateParams", function (lodash, $stateParams) {
    return {
      restrict: 'E',
      scope: {},
      bindToController: true,
      controllerAs: 'vm',
      templateUrl: 'templates/ceilometer-samples.tpl.html',
      controller: ["Ceilometer", function controller(Ceilometer) {
        var _this = this;

        // console.log(Ceilometer.selectResource);

        this.chartColors = ['#286090', '#F7464A', '#46BFBD', '#FDB45C', '#97BBCD', '#4D5360', '#8c4f9f'];

        this.chart = {
          series: [],
          labels: [],
          data: []
        };

        Chart.defaults.global.colours = this.chartColors;

        this.chartType = 'line';

        if ($stateParams.name && $stateParams.tenant) {
          this.name = $stateParams.name;
          this.tenant = $stateParams.tenant;
          // TODO rename tenant in resource_id
        } else {
            throw new Error('Missing Name and Tenant Params!');
          }

        /**
         * Goes trough the array and format date to be used as labels
         *
         * @param Array data
         * @returns Array a list of labels
         */

        this.getLabels = function (data) {
          return data.reduce(function (list, item) {
            var date = new Date(item.timestamp);
            list.push(date.getHours() + ':' + ((date.getMinutes() < 10 ? '0' : '') + date.getMinutes()) + ':' + date.getSeconds());
            return list;
          }, []);
        };

        /**
         * Goes trough the array and return a flat array of values
         *
         * @param Array data
         * @returns Array a list of values
         */

        this.getData = function (data) {
          return data.reduce(function (list, item) {
            list.push(item.volume);
            return list;
          }, []);
        };

        /**
         * Add a samples to the chart
         *
         * @param string resource_id
         */
        this.chartMeters = [];
        this.addMeterToChart = function (resource_id) {
          _this.chart['labels'] = _this.getLabels(lodash.sortBy(_this.samplesList[resource_id], 'timestamp'));
          _this.chart['series'].push(resource_id);
          _this.chart['data'].push(_this.getData(lodash.sortBy(_this.samplesList[resource_id], 'timestamp')));
          _this.chartMeters.push(_this.samplesList[resource_id][0]); //use the 0 as are all samples for the same resource and I need the name
          lodash.remove(_this.sampleLabels, { id: resource_id });
        };

        this.removeFromChart = function (meter) {
          _this.chart.data.splice(_this.chart.series.indexOf(meter.resource_id), 1);
          _this.chart.series.splice(_this.chart.series.indexOf(meter.resource_id), 1);
          _this.chartMeters.splice(lodash.findIndex(_this.chartMeters, { resource_id: meter.resource_id }), 1);
          _this.sampleLabels.push({
            id: meter.resource_id,
            name: meter.resource_name || meter.resource_id
          });
        };

        /**
         * Format samples to create a list of labels and ids
         */

        this.formatSamplesLabels = function (samples) {

          return lodash.uniq(samples, 'resource_id').reduce(function (labels, item) {
            labels.push({
              id: item.resource_id,
              name: item.resource_name || item.resource_id
            });

            return labels;
          }, []);
        };

        /**
         * Load the samples and format data
         */

        this.showSamples = function () {
          _this.loader = true;
          // Ceilometer.getSamples(this.name, this.tenant) //fetch one
          Ceilometer.getSamples(_this.name) //fetch all
          .then(function (res) {

            // rename things in UI
            res.map(function (m) {
              m.resource_name = m.resource_name.replace('mysite_onos_vbng', 'ONOS_FABRIC');
              m.resource_name = m.resource_name.replace('mysite_onos_volt', 'ONOS_CORD');
              m.resource_name = m.resource_name.replace('mysite_vbng', 'mysite_vRouter');
              return m;
            });
            // end rename things in UI

            // setup data for visualization
            _this.samplesList = lodash.groupBy(res, 'resource_id');
            _this.sampleLabels = _this.formatSamplesLabels(res);

            // add current meter to chart
            _this.addMeterToChart(_this.tenant);
          })['catch'](function (err) {
            _this.error = err.data.detail;
          })['finally'](function () {
            _this.loader = false;
          });
        };

        this.showSamples();
      }]
    };
  }]);
})();
/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 3/21/16.
 */

'use strict';

(function () {
  'use strict';

  angular.module('xos.ceilometerDashboard').service('Ceilometer', ["$http", "$q", function ($http, $q) {

    this.getMappings = function () {
      var deferred = $q.defer();

      $http.get('/xoslib/xos-slice-service-mapping/').then(function (res) {
        deferred.resolve(res.data);
      })['catch'](function (e) {
        deferred.reject(e);
      });

      return deferred.promise;
    };

    this.getMeters = function (params) {
      var deferred = $q.defer();

      $http.get('/xoslib/meters/', { cache: true, params: params })
      // $http.get('../meters_mock.json', {cache: true})
      .then(function (res) {
        deferred.resolve(res.data);
      })['catch'](function (e) {
        deferred.reject(e);
      });

      return deferred.promise;
    };

    this.getSamples = function (name, tenant) {
      var deferred = $q.defer();

      $http.get('/xoslib/metersamples/', { params: { meter: name, tenant: tenant } }).then(function (res) {
        deferred.resolve(res.data);
      })['catch'](function (e) {
        deferred.reject(e);
      });

      return deferred.promise;
    };

    this.getStats = function (options) {
      var deferred = $q.defer();

      $http.get('/xoslib/meterstatistics/', { cache: true, params: options })
      // $http.get('../stats_mock.son', {cache: true})
      .then(function (res) {
        deferred.resolve(res.data);
      })['catch'](function (e) {
        deferred.reject(e);
      });

      return deferred.promise;
    };

    // hold dashboard status (opened service, slice, resource)
    this.selectedService = null;
    this.selectedSlice = null;
    this.selectedResource = null;
  }]);
})();
/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 3/21/16.
 */

'use strict';

(function () {
  'use strict';

  angular.module('xos.ceilometerDashboard').directive('ceilometerDashboard', ["lodash", function (lodash) {
    return {
      restrict: 'E',
      scope: {},
      bindToController: true,
      controllerAs: 'vm',
      templateUrl: 'templates/ceilometer-dashboard.tpl.html',
      controller: ["Ceilometer", function controller(Ceilometer) {
        var _this = this;

        this.showStats = false;

        // this open the accordion
        this.accordion = {
          open: {}
        };

        /**
         * Open the active panel base on the service stored values
         */
        this.openPanels = function () {
          if (Ceilometer.selectedService) {
            _this.accordion.open[Ceilometer.selectedService] = true;
            if (Ceilometer.selectedSlice) {
              _this.loadSliceMeter(Ceilometer.selectedSlice, Ceilometer.selectedService);
              _this.selectedSlice = Ceilometer.selectedSlice;
              if (Ceilometer.selectedResource) {
                _this.selectedResource = Ceilometer.selectedResource;
              }
            }
          }
        };

        /**
         * Load the list of service and slices
         */
        this.loadMappings = function () {
          _this.loader = true;
          Ceilometer.getMappings().then(function (services) {

            // rename thing in UI
            services.map(function (service) {
              if (service.service === 'service_ONOS_vBNG') {
                service.service = 'ONOS_FABRIC';
              }
              if (service.service === 'service_ONOS_vOLT') {
                service.service = 'ONOS_CORD';
              }

              service.slices.map(function (s) {
                if (s.slice === 'mysite_onos_volt') {
                  s.slice = 'ONOS_CORD';
                }
                if (s.slice === 'mysite_onos_vbng') {
                  s.slice = 'ONOS_FABRIC';
                }
                if (s.slice === 'mysite_vbng') {
                  s.slice = 'mysite_vRouter';
                }
              });

              return service;
            });
            // end rename thing in UI

            _this.services = services;
            _this.openPanels();
          })['catch'](function (err) {
            _this.error = err.data && err.data.detail ? err.data.detail : 'An Error occurred. Please try again later.';
          })['finally'](function () {
            _this.loader = false;
          });
        };

        this.loadMappings();

        /**
         * Load the list of a single slice
         */
        this.loadSliceMeter = function (slice, service_name) {

          Ceilometer.selectedSlice = null;
          Ceilometer.selectedService = null;
          Ceilometer.selectedResources = null;

          // visualization info
          _this.loader = true;
          _this.error = null;
          _this.ceilometerError = null;

          Ceilometer.getMeters({ tenant: slice.project_id }).then(function (sliceMeters) {
            _this.selectedSlice = slice.slice;
            _this.selectedTenant = slice.project_id;

            // store the status
            Ceilometer.selectedSlice = slice;
            Ceilometer.selectedService = service_name;

            // rename things in UI
            sliceMeters.map(function (m) {
              m.resource_name = m.resource_name.replace('mysite_onos_vbng', 'ONOS_FABRIC');
              m.resource_name = m.resource_name.replace('mysite_onos_volt', 'ONOS_CORD');
              m.resource_name = m.resource_name.replace('mysite_vbng', 'mysite_vRouter');
              return m;
            });
            // end rename things in UI

            _this.selectedResources = lodash.groupBy(sliceMeters, 'resource_name');

            // hacky
            if (Ceilometer.selectedResource) {
              _this.selectedMeters = _this.selectedResources[Ceilometer.selectedResource];
            }
          })['catch'](function (err) {

            // this means that ceilometer is not yet ready
            if (err.status === 503) {
              return _this.ceilometerError = err.data.detail.specific_error;
            }

            _this.ceilometerError = err.data && err.data.detail && err.data.detail.specific_error ? err.data.detail.specific_error : 'An Error occurred. Please try again later.';
          })['finally'](function () {
            _this.loader = false;
          });
        };

        /**
         * Select Meters for a resource
         *
         * @param Array meters The list of selected resources
         * @returns void
         */
        this.selectedMeters = null;
        this.selectMeters = function (meters, resource) {
          _this.selectedMeters = meters;

          Ceilometer.selectedResource = resource;
          _this.selectedResource = resource;
        };
      }]
    };
  }]);
})();