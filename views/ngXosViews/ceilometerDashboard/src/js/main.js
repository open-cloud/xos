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

  this.getMeters = () => {
    let deferred = $q.defer();

    $http.get('/xoslib/meters/', {cache: true})
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

  this.getStats = (sliceName) => {
    let deferred = $q.defer();

    $http.get('/xoslib/meterstatistics/', {cache: true})
    // $http.get('../stats_mock.son', {cache: true})
    .then((res) => {
      deferred.resolve(lodash.filter(res.data, {slice: sliceName}))
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

      // this open the accordion
      this.accordion = {
        open: {}
      };

      /**
      * Open the active panel base on the service stored values
      */
      this.openPanels = () => {
        if(Ceilometer.selectedService){
          this.accordion.open[Ceilometer.selectedService] = true;
          if(Ceilometer.selectedSlice){
            this.selectedSlice = Ceilometer.selectedSlice;
            this.selectedResources = this.projects[Ceilometer.selectedService][Ceilometer.selectedSlice]
            if(Ceilometer.selectedResource){
              this.selectedResource = Ceilometer.selectedResource;
              this.selectedMeters = this.selectedResources[Ceilometer.selectedResource];
            }
          }
        }
      }

      this.loadMeters = () => {
        this.loader = true;

        // TODO rename projects in meters
        Ceilometer.getMeters()
        .then(meters => {
          //group project by service
          this.projects = lodash.groupBy(meters, 'service');
          lodash.forEach(Object.keys(this.projects), (project) => {
            // inside each service group by slice
            this.projects[project] = lodash.groupBy(this.projects[project], 'slice');
            lodash.forEach(Object.keys(this.projects[project]), (slice) => {
              // inside each service => slice group by resource
              this.projects[project][slice] = lodash.groupBy(this.projects[project][slice], 'resource_name');
            });
          });

          // open selected panels
          this.openPanels();
        })
        .catch(err => {
          this.error = err.data.detail;
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
      this.selectResources = (resources, slice, service) => {
        //cleaning
        this.selectedResources = null;
        this.selectedResource = null;
        this.selectedMeters = null;

        // hold the resource list for the current slice
        this.selectedResources = resources;
        this.selectedSlice = slice;
        this.selectedService = service;

        // store the status
        Ceilometer.selectedSlice = slice;
        Ceilometer.selectedService = service;
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

        Ceilometer.selectedResource = resource;
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
  // NOTE reading this on demand for a single
.directive('ceilometerStats', function(){
  return {
    restrict: 'E',
    scope: {
      name: '=name',
    },
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/ceilometer-stats.tpl.html',
    controller: function($scope, Ceilometer) {
      this.getStats = () => {
        this.loader = true;
        Ceilometer.getStats(this.name)
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

      this.getStats();

      $scope.$watch(() => this.name, () => {this.getStats();});
    }
  }
})
.filter('orderObjectByKey', function(lodash) {
  return function(items) {

    if(!items){
      return;
    }

    return lodash.reduce(Object.keys(items).reverse(), (list, key) => {
      list[key] = items[key];
      return list;
    }, {});

  };
});
;