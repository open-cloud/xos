'use strict';

angular.module('xos.dashboardManager', [
  'ngResource',
  'ngCookies',
  'ui.router',
  'xos.helpers',
  'dndLists'
])
.config(($stateProvider) => {
  $stateProvider
  .state('manage-user-dashboards', {
    url: '/',
    template: '<user-dashboards></user-dashboards>'
  })
  .state('add-dashboards', {
    url: '/add',
    template: '<dashboard-form></dashboard-form>'
  })
  .state('edit-dashboards', {
    url: '/dashboards/:id',
    template: '<dashboard-form></dashboard-form>'
  });
})
.config(function($httpProvider){
  $httpProvider.interceptors.push('NoHyperlinks');
})
.service('UserDashboards', function($http, $q){
  this.query = () => {
    const d = $q.defer();

    $http.get('/api/utility/dashboards')
    .then(res => {
      d.resolve(res.data);
    })
    .catch(err => {
      d.reject(err);
    });

    return {$promise: d.promise};
  }

  this.update = (dashboard) => {
    const d = $q.defer();
    $http.post('/api/utility/dashboards/', dashboard)
    .then(res => {
      d.resolve(res.data);
    })
    .catch(err => {
      d.reject(err);
    });

    return {$promise: d.promise};
  }
});