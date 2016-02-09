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
  .state('home', {
    url: '/',
    template: '<diagnostic></diagnostic>'
  });
})
.config(function($httpProvider){
  $httpProvider.interceptors.push('NoHyperlinks');
});
