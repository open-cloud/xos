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
            label: 'First Name',
            prop: 'firstname'
          },
          {
            label: 'Last Name',
            prop: 'lastname'
          }
        ],
        classes: 'table table-striped table-condensed',
        actions: [
          {
            label: 'delete',
            icon: 'remove',
            cb: (user) => {
              console.log(user);
            },
            color: 'red'
          }
        ],
        filter: 'field',
        order: true,
        pagination: {
          pageSize: 6
        }
      };

      // retrieving user list
      Users.query().$promise
      .then((users) => {
        this.users = users.concat(users, users, users);
      })
      .catch((e) => {
        throw new Error(e);
      });
    }
  };
});