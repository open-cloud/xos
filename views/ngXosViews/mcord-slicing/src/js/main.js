
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

angular.module('xos.mcord-slicing', [
  'ngResource',
  'ngCookies',
  'ui.router',
  'xos.helpers'
])
.config(($stateProvider) => {
  $stateProvider
  .state('slicing-topo', {
    url: '/',
    template: '<slicing-topo></slicing-topo>'
  })
  .state('node-links', {
    url: '/data',
    template: '<node-links></node-links>'
  });
})
.config(function($httpProvider){
  $httpProvider.interceptors.push('NoHyperlinks');
})
.service('McordSlicingTopo', function($http, $q){
  this.query = () => {
    const d = $q.defer();

    $http.get('api/service/mcord_slicing_ui/topology/')
    .then((res) => {
      let data;
      if (res.data.hasOwnProperty('nodes')){
        data = res.data;
      }
      else {
        // INVESTIGATE why proxy change resposne
        data = {
          nodes: res.data[0],
          links: res.data[1]
        };
      }
      d.resolve(data);
    })
    .catch((e) => {
      d.reject(e);
    });

    return {$promise: d.promise};
  };
})
.directive('nodeLinks', function(){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/node-links.tpl.html',
    controller: function(McordSlicingTopo){

      this.tableConfig = {
        columns: [
          {
            label: 'Id',
            prop: 'id'
          },
          {
            label: 'Name',
            prop: 'name'
          },
          {
            label: 'Type',
            prop: 'type'
          },
          {
            label: 'Plane',
            prop: 'plane'
          },
          {
            label: 'Model Id',
            prop: 'model_id'
          }
        ]
      };
      
      // retrieving user list
      McordSlicingTopo.query().$promise
      .then((users) => {
        this.users = users.nodes;
      })
      .catch((e) => {
        throw new Error(e);
      });
    }
  };
});