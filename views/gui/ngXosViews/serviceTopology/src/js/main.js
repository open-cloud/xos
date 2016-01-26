'use strict';

angular.module('xos.serviceTopology', [
  'ngResource',
  'ngCookies',
  'ngLodash',
  'ngAnimate',
  'ui.router',
  'xos.helpers'
])
.config(($stateProvider) => {
  $stateProvider
  .state('user-list', {
    url: '/',
    template: '<service-canvas></service-canvas>'
  });
})
.config(function($httpProvider){
  $httpProvider.interceptors.push('NoHyperlinks');
});
