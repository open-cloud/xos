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

      this.smartTableConfig = {
        resource: 'Subscribers'
      };

      this.formConfig = {
        exclude: ['password', 'last_login'],
        formName: 'sampleForm',
        actions: [
          {
            label: 'Save',
            icon: 'ok', // refers to bootstraps glyphicon
            cb: (user) => { // receive the model
              console.log(user);
            },
            class: 'success'
          }
        ]
      };
      
      // retrieving user list
      Subscribers.query().$promise
      .then((users) => {
        this.users = users[0];
      })
      .catch((e) => {
        throw new Error(e);
      });
    }
  };
});