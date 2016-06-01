'use strict';

angular.module('xos.subscribers', [
  'ngResource',
  'ngCookies',
  'ui.router',
  'xos.helpers'
])
.config(($stateProvider) => {
  $stateProvider
  .state('user-list', {
    url: '/',
    template: '<subscribers-list></subscribers-list>'
  });
})
.config(function($httpProvider){
  $httpProvider.interceptors.push('NoHyperlinks');
})
.directive('subscribersList', function(){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/subscribers-list.tpl.html',
    controller: function(){

      this.smartTableConfig = {
        resource: 'Subscribers'
      };
    }
  };
});