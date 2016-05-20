'use strict';

angular.module('xos.ceilometerDashboard', [
  'ngResource',
  'ngCookies',
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
});
