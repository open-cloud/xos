
/*
 * Copyright 2017-present Open Networking Foundation

 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at

 * http://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


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