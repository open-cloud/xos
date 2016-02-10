'use strict';

angular.module('xos.ceilometerDashboard', [
  'ngResource',
  'ngCookies',
  'ngLodash',
  'ui.router',
  'xos.helpers',
  'ngAnimate',
  'chart.js',
  'ui.bootstrap.accordion'
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
  });
  $urlRouterProvider.otherwise('/');
})
.config(function($httpProvider){
  $httpProvider.interceptors.push('NoHyperlinks');
})
.run(function($rootScope){
  $rootScope.stateName = 'ceilometerDashboard';
  $rootScope.$on('$stateChangeStart', (event, toState) => {
    $rootScope.stateName = toState.name;
  })
})
.service('Ceilometer', function($http, $q, lodash){

  this.getMappings = () => {
    let deferred = $q.defer();

    $http.get('/xoslib/xos-slice-service-mapping/')
    .then((res) => {
      deferred.resolve(res.data)
    })
    .catch((e) => {
      deferred.reject(e);
    });

    return deferred.promise;
  }

  this.getMeters = (params) => {
    let deferred = $q.defer();

    $http.get('/xoslib/meters/', {cache: true, params: params})
    // $http.get('../meters_mock.json', {cache: true})
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

  this.getStats = (options) => {
    let deferred = $q.defer();

    $http.get('/xoslib/meterstatistics/', {cache: true, params: options})
    // $http.get('../stats_mock.son', {cache: true})
    .then((res) => {
      deferred.resolve(res.data);
    })
    .catch((e) => {
      deferred.reject(e);
    });

    return deferred.promise;
  };

  // hold dashboard status (opened service, slice, resource)
  this.selectedService = null;
  this.selectedSlice = null;
  this.selectedResource = null;
})
.directive('ceilometerDashboard', function(lodash){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/ceilometer-dashboard.tpl.html',
    controller: function(Ceilometer){

      this.showStats = false;

      // this open the accordion
      this.accordion = {
        open: {}
      }

      /**
      * Open the active panel base on the service stored values
      */
      this.openPanels = () => {
        if(Ceilometer.selectedService){
          this.accordion.open[Ceilometer.selectedService] = true;
          if(Ceilometer.selectedSlice){
            this.loadSliceMeter(Ceilometer.selectedSlice, Ceilometer.selectedService);
            this.selectedSlice = Ceilometer.selectedSlice;
            if(Ceilometer.selectedResource){
              this.selectedResource = Ceilometer.selectedResource;
            }
          }
        }
      }

      /**
      * Load the list of service and slices
      */

      this.loadMappings = () => {
        this.loader = true;
        Ceilometer.getMappings()
        .then((services) => {
          this.services = services;
          this.openPanels();
        })
        .catch(err => {
          this.error = (err.data && err.data.detail) ? err.data.detail : 'An Error occurred. Please try again later.';
        })
        .finally(() => {
          this.loader = false;
        });
      };

      this.loadMappings();

      /**
      * Load the list of a single slice
      */
     
      this.loadSliceMeter = (slice, service_name) => {

        Ceilometer.selectedSlice = null;
        Ceilometer.selectedService = null;
        Ceilometer.selectedResources = null;

        // visualization info
        this.loader = true;
        this.selectedSlice = slice.slice;
        this.selectedTenant = slice.project_id;

        // store the status
        Ceilometer.selectedSlice = slice;
        Ceilometer.selectedService = service_name;

        Ceilometer.getMeters({tenant: slice.project_id})
        .then((sliceMeters) => {
          this.selectedResources = lodash.groupBy(sliceMeters, 'resource_name');

          // hacky
          if(Ceilometer.selectedResource){
            this.selectedMeters = this.selectedResources[Ceilometer.selectedResource];
          }
        })
        .catch(err => {
          this.error = (err.data && err.data.detail) ? err.data.detail : 'An Error occurred. Please try again later.';
        })
        .finally(() => {
          this.loader = false;
        });
      };

      /**
      * Select Meters for a resource
      *
      * @param Array meters The list of selected resources
      * @returns void
      */
      this.selectedMeters = null;
      this.selectMeters = (meters, resource) => {
        this.selectedMeters = meters;

        Ceilometer.selectedResource = resource;
        this.selectedResource = resource;
      }

    }
  };
})
.directive('ceilometerSamples', function(lodash, $stateParams){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/ceilometer-samples.tpl.html',
    controller: function(Ceilometer) {

      // console.log(Ceilometer.selectResource);

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
        // TODO rename tenant in project_id
      }
      else{
        throw new Error('Missing Name and Tenant Params!');
      }

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
      this.addMeterToChart = (project_id) => {
        this.chart['labels'] = this.getLabels(lodash.sortBy(this.samplesList[project_id], 'timestamp'));
        this.chart['series'].push(project_id);
        this.chart['data'].push(this.getData(lodash.sortBy(this.samplesList[project_id], 'timestamp')));
        this.chartMeters.push(this.samplesList[project_id][0]); //use the 0 as are all samples for the same resource and I need the name
        lodash.remove(this.sampleLabels, {id: project_id});
      }

      this.removeFromChart = (meter) => {
        this.chart.data.splice(this.chart.series.indexOf(meter.project_id), 1);
        this.chart.series.splice(this.chart.series.indexOf(meter.project_id), 1);
        this.chartMeters.splice(lodash.findIndex(this.chartMeters, {project_id: meter.project_id}), 1);
        this.sampleLabels.push({
          id: meter.project_id,
          name: meter.resource_name || meter.project_id
        })
      };

      /**
      * Format samples to create a list of labels and ids
      */
     
      this.formatSamplesLabels = (samples) => {

        return lodash.uniq(samples, 'project_id')
        .reduce((labels, item) => {
          labels.push({
            id: item.project_id,
            name: item.resource_name || item.project_id
          });
          return labels;
        }, []);
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
          this.samplesList = lodash.groupBy(res, 'project_id');
          this.sampleLabels = this.formatSamplesLabels(res);
          
          // add current meter to chart
          this.addMeterToChart(this.tenant);

        })
        .catch(err => {
          this.error = err.data.detail;
        })
        .finally(() => {
          this.loader = false;
        });
      };

      this.showSamples();
    }
  }
})
.directive('ceilometerStats', function(){
  return {
    restrict: 'E',
    scope: {
      name: '=name',
      tenant: '=tenant'
    },
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/ceilometer-stats.tpl.html',
    controller: function($scope, Ceilometer) {

      this.getStats = (tenant) => {
        this.loader = true;
        Ceilometer.getStats({tenant: tenant})
        .then(res => {
          this.stats = res;
        })
        .catch(err => {
          this.error = err.data;
        })
        .finally(() => {
          this.loader = false;
        });
      };

      $scope.$watch(() => this.name, (val) => {
        if(val){
          this.getStats(this.tenant);
        }
      });
    }
  }
});