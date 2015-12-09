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

  this.sliceDetails = {};

  this.formatSliceDetails = (meters) => {

  };

  this.getMeters = () => {
    let deferred = $q.defer();

    // $http.get('/xoslib/meters/', {cache: true})
    $http.get('../meters_mock.json', {cache: true})
    .then((res) => {
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
          //group project by service
          this.projects = lodash.groupBy(meters, 'service');
          lodash.forEach(Object.keys(this.projects), (project) => {
            // inside each service group by slice
            this.projects[project] = lodash.groupBy(this.projects[project], 'slice');
            lodash.forEach(Object.keys(this.projects[project]), (slice) => {
              // inside each service => slice group by resource
              this.projects[project][slice] = lodash.groupBy(this.projects[project][slice], 'resource_id');
            });
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
      * Select the current service
      */
     
      this.selectService = (service) => {
        //cleaning
        this.selectedResources = null;
        this.selectedResource = null;
        this.selectedMeters = null;
        
        this.selectedService = service;
      };

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

      this.chartColors = [
        '#286090',
        '#F7464A',
        '#46BFBD',
        '#FDB45C',
        '#97BBCD',
        '#4D5360',
        '#8c4f9f'
      ];

      this.chart = {
        series: [],
        labels: [],
        data: []
      }

      Chart.defaults.global.colours = this.chartColors;
      
      this.chartType = 'line';

      if($stateParams.name && $stateParams.tenant){
        this.name = $stateParams.name;
        this.tenant = $stateParams.tenant;
      }

      // Mock

      /**
      * Goes trough the array and format date to be used as labels
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
      * Goes trough the array and return a flat array of values
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

      /**
      * Add a samples to the chart
      *
      * @param string resource_id
      */
      this.chartMeters = [];
      this.addMeterToChart = (resource_id) => {
        this.chart['labels'] = this.getLabels(lodash.sortBy(this.samplesList[resource_id], 'timestamp'));
        this.chart['series'].push(resource_id);
        this.chart['data'].push(this.getData(lodash.sortBy(this.samplesList[resource_id], 'timestamp')));
        this.chartMeters.push(resource_id);
        lodash.remove(this.sampleLabels, {id: resource_id});
      }

      this.removeFromChart = (resource_id) => {
        this.chart.data.splice(this.chart.series.indexOf(resource_id), 1);
        this.chart.series.splice(this.chart.series.indexOf(resource_id), 1);
        this.chartMeters.splice(this.chartMeters.indexOf(resource_id), 1);
        this.sampleLabels.push({
          id: resource_id,
          // TODO add resource name
        })
      };

      /**
      * Format samples to create a list of labels and ids
      */
     
      this.formatSamplesLabels = (samples) => {

        return lodash.uniq(samples.reduce((labels, item) => {
          labels.push({
            id: item.resource_id,
            // TODO add resource name
          });
          return labels;
        }, []), item => item.id);
      }


      /**
      * Load the samples and format data
      */

      this.showSamples = () => {
        this.loader = true;
        // Ceilometer.getSamples(this.name, this.tenant) //fetch one
        Ceilometer.getSamples(this.name) //fetch all
        .then(res => {

          // setup data for visualization
          this.samplesList = lodash.groupBy(res, 'resource_id');
          this.sampleLabels = this.formatSamplesLabels(res);
          
          // add current meter to chart
          this.addMeterToChart(this.tenant);

        })
        .catch(err => {
          this.error = err.data.detail;
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