'use strict';

angular.module('xos.sampleView', [
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
    template: '<users-list></users-list>'
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
    controller: function(Users){

      this.tableConfig = {
        columns: [
          {
            label: 'E-Mail',
            prop: 'email'
          },
          {
            label: 'E-Mail',
            prop: 'firstname'
          },
          {
            label: 'E-Mail',
            prop: 'lastname'
          }
        ],
        classes: 'table table-striped table-condensed'
      };

      // retrieving user list
      Users.query().$promise
      .then((users) => {
        this.users = users;
      })
      .catch((e) => {
        throw new Error(e);
      });
    }
  };
});