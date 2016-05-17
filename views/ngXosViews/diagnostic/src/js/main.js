(function () {
  'use strict';

  angular.module('xos.diagnostic', [
    'ngResource',
    'ngCookies',
    'ngAnimate',
    'ui.router',
    'xos.helpers'
  ])
  .config(($stateProvider) => {
    $stateProvider
    .state('home', {
      url: '/',
      template: '<diagnostic-container></diagnostic-container>'
    });
  })
  .config(function($httpProvider){
    $httpProvider.interceptors.push('NoHyperlinks');
  })
  .run(($log) => {
    $log.info('Diagnostic Started');
  });

})();