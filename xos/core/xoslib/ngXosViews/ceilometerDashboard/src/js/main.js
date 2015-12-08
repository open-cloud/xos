'use strict';

angular.module('xos.ceilometerDashboard', [
  'ngResource',
  'ngCookies',
  'ngLodash',
  'ui.router',
  'xos.helpers',
  'ngAnimate',
  'chart.js'
])
.config(($stateProvider, $urlRouterProvider) => {
  $stateProvider
  .state('ceilometerDashboard', {
    url: '/',
    template: '<ceilometer-dashboard></ceilometer-dashboard>'
  })
  .state('samples', {
    url: '/:name/:tenant/samples',
    template: '<ceilometer-samples></ceilometer-samples>'
  })
  .state('split', {
    url: '/split',
    controller: () => {
      console.log('split', Split);
      Split(['#one', '#two', '#three'], {
        
      });
    },
    templateUrl: 'templates/split.html'
  });
  $urlRouterProvider.otherwise('/');
})
.config(function($httpProvider){
  $httpProvider.interceptors.push('NoHyperlinks');
})
.run(function($rootScope){
  $rootScope.stateName = 'ceilometerDashboard';
  $rootScope.$on('$stateChangeStart', (event, toState) => {
    console.log(toState.name);
    $rootScope.stateName = toState.name;
  })
})
.service('Ceilometer', function($http, $q){
  this.getMeters = () => {
    let deferred = $q.defer();

    // $http.get('/xoslib/meters/', {cache: true})
    $http.get('../meters_mock.json', {cache: true})
    .then((res) => {
      console.log(res.data);
      deferred.resolve(res.data)
    })
    .catch((e) => {
      deferred.reject(e);
    });

    return deferred.promise;
  }

  this.getSamples = (name, tenant) => {
    let deferred = $q.defer();

    $http.get(`/xoslib/metersamples/`, {params: {meter: name, tenant: tenant}})
    .then((res) => {
      deferred.resolve(res.data)
    })
    .catch((e) => {
      deferred.reject(e);
    });

    return deferred.promise;
  }
})
.directive('ceilometerDashboard', function(lodash){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/ceilometer-dashboard.tpl.html',
    controller: function(Ceilometer){

      this.loadMeters = () => {
        this.loader = true;

        Ceilometer.getMeters()
        .then(meters => {
          this.projects = lodash.groupBy(meters, 'project_name');
          lodash.forEach(Object.keys(this.projects), (project) => {
            this.projects[project] = lodash.groupBy(this.projects[project], 'resource_id');
          });
        })
        .catch(err => {
          this.err = err;
        })
        .finally(() => {
          this.loader = false;
        });
      }

      this.loadMeters();

      /**
      * Select Resources for a slice
      *
      * @param Array resources The list of selected resources
      * @returns void
      */
      this.selectedResources = null;
      this.selectResources = (resources, slice) => {
        //cleaning
        this.selectedResources = null;
        this.selectedResource = null;
        this.selectedMeters = null;

        this.selectedResources = resources;
        this.selectedSlice = slice;
      }

      /**
      * Select Meters for a resource
      *
      * @param Array meters The list of selected resources
      * @returns void
      */
      this.selectedMeters = null;
      this.selectMeters = (meters, resource) => {
        this.selectedMeters = meters;
        this.selectedResource = resource;
      }

    }
  };
})
.directive('ceilometerSamples', function(lodash, $stateParams){
  return {
    restrict: 'E',
    scope: {
      name: '=name',
      tenant: '=tenant'
    },
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/ceilometer-samples.tpl.html',
    controller: function(Ceilometer) {

      this.chartType = 'line';

      if($stateParams.name && $stateParams.tenant){
        this.name = $stateParams.name;
        this.tenant = $stateParams.tenant;
      }

      // Mock

      /**
      * Goe trough the array and format date to be used as labels
      *
      * @param Array data
      * @returns Array a list of labels
      */

      this.getLabels = (data) => {
        return data.reduce((list, item) => {
          let date = new Date(item.timestamp);
          list.push(`${date.getHours()}:${(date.getMinutes()<10?'0':'') + date.getMinutes()}:${date.getSeconds()}`);
          return list;
        }, []);
      };

      /**
      * Goe trough the array and return a flat array of values
      *
      * @param Array data
      * @returns Array a list of values
      */

      this.getData = (data) => {
        return data.reduce((list, item) => {
          list.push(item.volume);
          return list;
        }, []);
      }

      this.addMeterToChart = (project_id) => {
        this.chart['series'].push(project_id);
        this.chart['data'].push(this.getData(this.samplesList[project_id]))
      }

      /**
      * Load the samples and format data
      */

      this.showSamples = () => {
        this.loader = true;
        // Ceilometer.getSamples(this.name, this.tenant) //fetch one
        Ceilometer.getSamples(this.name) //fetch all
        .then(res => {
          this.samplesList = lodash.groupBy(res, 'project_id');
          res = lodash.sortBy(this.samplesList[this.tenant], 'timestamp');
          this.chart = {
            series: [this.tenant],
            labels: this.getLabels(res),
            data: [this.getData(res)]
          }
        })
        .catch(err => {
          console.warn(err);
        })
        .finally(() => {
          this.loader = false;
        });
      };

      this.showSamples();
    }
  }
});