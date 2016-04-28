'use strict';

angular.module('xos.<%= name %>', [
  'ngResource',
  'ngCookies',
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
            label: 'First Name',
            prop: 'firstname'
          },
          {
            label: 'Last Name',
            prop: 'lastname'
          },
          {
            label: 'Created',
            prop: 'created'
          },
          {
            label: 'Is Admin',
            prop: 'is_admin'
          }
        ]
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