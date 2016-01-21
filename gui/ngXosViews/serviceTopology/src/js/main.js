'use strict';

angular.module('xos.serviceTopology', [
  'ngResource',
  'ngCookies',
  'ngLodash',
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
})
.directive('usersList', function(){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/users-list.tpl.html',
    controller: function(Services){
      // retrieving user list
      Services.query().$promise
      .then((res) => {
        console.log(res);
      })
      .catch((e) => {
        throw new Error(e);
      });
    }
  };
});