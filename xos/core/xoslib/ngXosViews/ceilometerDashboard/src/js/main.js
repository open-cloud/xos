'use strict';

angular.module('xos.ceilometerDashboard', [
  'ngResource',
  'ngCookies',
  'ngLodash',
  'ui.router',
  'xos.helpers',
  'angularCharts'
])
.config(($stateProvider) => {
  $stateProvider
  .state('ceilometerDashboard', {
    url: '/',
    template: '<ceilometer-dashboard></ceilometer-dashboard>'
  })
  .state('samples', {
    url: '/:name/:tenant/samples',
    template: '<ceilometer-samples></ceilometer-samples>'
  });
})
.config(function($httpProvider){
  $httpProvider.interceptors.push('NoHyperlinks');
})
.service('Ceilometer', function($http, $q){
  this.getMeters = () => {
    let deferred = $q.defer();

    $http.get('xoslib/meters/', {cache: true})
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

    $http.get(`xoslib/metersamples/`, {params: {meter: name, tenant: tenant}})
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

      if($stateParams.name && $stateParams.tenant){
        this.name = $stateParams.name;
        this.tenant = $stateParams.tenant;
      }

      this.formatDateLabels = (date) => {
        // date = new Date(date);
        // return `${date.getMonth()}/${date.getYear()}`
        return date;
      };

      this.formatSamplesData = (data) => {

        let formatted = [];

        lodash.forEach(data, (item) => {
          formatted.push({
            x: this.formatDateLabels(item.timestamp),
            y: [item.volume]
          });
        });

        return lodash.sortBy(formatted, 'timestamp');
      }

      this.showSamples = () => {
        this.loader = true;
        Ceilometer.getSamples(this.name, this.tenant)
        .then(res => {
          console.log(res.length, lodash.groupBy(res, 'timestamp'));
          this.sampleChartData = {
            series: [$stateParams.name],
            data: this.formatSamplesData(res)
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

      this.sampleChartConfig = {
        title: false,
        tooltips: true,
        labels: false,
        legend: {
          display: false,
          //could be 'left, right'
          position: 'right'
        },
        lineLegend: 'traditional',
        waitForHeightAndWidth: true
      }
    }
  }
});