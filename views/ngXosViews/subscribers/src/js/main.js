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
    controller: function(Subscribers){

      this.tableConfig = {
        filter: 'field',
        order: true,
        pagination: {
          pageSize: 10
        },
        columns: [
          {
            label: 'Name',
            prop: 'humanReadableName'
          },
          {
            label: 'Identity',
            prop: 'identity',
            type: 'object'
          },
          {
            label: 'Related Info',
            prop: 'related',
            type: 'object'
          }
        ]
      };

      this.smartTableConfig = {
        resource: 'Subscribers'
      };
      
      // retrieving user list
      Subscribers.query().$promise
      .then((users) => {
        this.users = users;
      })
      .catch((e) => {
        throw new Error(e);
      });
    }
  };
});