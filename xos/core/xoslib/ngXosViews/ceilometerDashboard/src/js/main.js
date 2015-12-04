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
  });
})
.config(function($httpProvider){
  $httpProvider.interceptors.push('NoHyperlinks');
})
.service('Ceilometer', function($http, $q, $timeout){
  this.getMeters = () => {
    let deferred = $q.defer();

    $http.get('../mocks/meters.json')
    .then((res) => {
      $timeout(() => {
        deferred.resolve(res.data)
      }, 1000);
    })
    .catch((e) => {
      deferred.reject(e);
    });

    return deferred.promise;
  }
})
.directive('ceilometerDashboard', function(){
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
          this.meters = meters;
          console.log(meters.length);
        })
        .catch(err => {
          this.err = err;
        })
        .finally(() => {
          this.loader = false;
        });
      }

      this.loadMeters();

      // //sample chart
      // this.sampleChartData = {
      //   series: [
      //     'VM',
      //     'Containers',
      //     'Instances'
      //   ],
      //   data: [
      //     {
      //       x: 0,
      //       y: [
      //         479,
      //         54,
      //         213,
      //       ],
      //       tooltip: 'This is a tooltip'
      //     },
      //     {
      //       x: 1,
      //       y: [
      //         64,
      //         279,
      //         10,
      //       ],
      //       tooltip: 'This is another tooltip'
      //     },
      //     {
      //       x: 2,
      //       y: [
      //         136,
      //         19,
      //         259,
      //       ],
      //       tooltip: 'Third tooltip'
      //     }
      //   ]
      // };

      // this.sampleChartConfig = {
      //   title: false,
      //   tooltips: true,
      //   labels: false,
      //   legend: {
      //     display: true,
      //     //could be 'left, right'
      //     position: 'left'
      //   },
      //   lineLegend: 'lineEnd',
      //   waitForHeightAndWidth: true
      // }
    }
  };
});