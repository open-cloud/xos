/* global angular */
/* eslint-disable dot-location*/

// TODO
// - Add Cache
// - Refactor routing with ui.router and child views (share the navigation and header)

'use strict';

angular.module('xos.<%= name %>', [
  'ngResource',
  'ngRoute',
  'ngCookies',
  'ngLodash',
  'xos.helpers',
  'xos.xos'
])
.config(($routeProvider) => {

  $routeProvider
  .when('/', {
    template: '<users-list></users-list>',
  })
  .otherwise('/');
})
.config(function($httpProvider){
  // add X-CSRFToken header for update, create, delete (!GET)
  $httpProvider.interceptors.push('SetCSRFToken');
  $httpProvider.interceptors.push('NoHyperlinks');
})
.directive('usersList', function(xos){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/users-list.tpl.html',
    controller: function(){
      // creating the API object
      const api = new xos({domain: ''});

      // retrieving user list
      api.User_List_GET()
      .then((users) => {
        this.users = users;
      })
      .catch((e) => {
        throw new Error(e);
      });
    }
  };
});