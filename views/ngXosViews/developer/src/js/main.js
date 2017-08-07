
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

angular.module('xos.developer', [
  'ngResource',
  'ngCookies',
  'ui.router',
  'xos.helpers'
])
.config(($stateProvider) => {
  $stateProvider
  .state('developer', {
    url: '/',
    template: '<developer-dashboard></developer-dashboard>'
  });
})
.config(function($httpProvider){
  $httpProvider.interceptors.push('NoHyperlinks');
})
.directive('developerDashboard', function(){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/developer-dashboard.tpl.html',
    controller: function($scope, $timeout, SlicesPlus, Instances, _){

      this.instancePerSliceConfig = {
        data: [],
        groupBy: 'slice',
        legend: true,
        classes: 'instance per slice',
        labelFormatter: (labels) => {
          return labels.map(l => {
            return _.find(this.slices, {id: parseInt(l)}).name
          });
        }
      };

      this.instancePerSiteConfig = {
        data: [],
        groupBy: 'site',
        legend: true,
        classes: 'instance per site',
      };

      this.networkPerSliceConfig = {
        data: [],
        groupBy: 'name',
        legend: true,
        classes: 'network per slice',
      };

      this.tableConfig = {
        columns: [
          {
            label: 'Name',
            prop: 'name'
          },
          {
            label: 'Privileges',
            prop: 'current_user_roles',
            type: 'array'
          },
          {
            label: 'Number of Instances (active / total)',
            type: 'custom',
            formatter: item => `${item.instance_total_ready} / ${item.instance_total}`
          },
          {
            label: 'Active Instances per Sites',
            type: 'object',
            prop: 'instance_distribution_ready'
          },
          {
            label: 'Total Instances per Sites',
            type: 'object',
            prop: 'instance_distribution'
          },
          {
            label: 'Networks',
            type: 'custom',
            formatter: item => item.networks.length
          }
        ]
      };

      // retrieving user list
      SlicesPlus.query().$promise
      .then((slices) => {
        this.slices = slices;
        return Instances.query().$promise
      })
      .then(instances => {
        
        // formatting data in this way sucks.
        // Provide a way to just pass data to the chart if needed [smartPie].

        // retrieving network per slices
        let networkPerSlice = _.reduce(this.slices, (list, s) => {
          if( s.networks.length > 1){
            // push s.neworks.length values in array
            for(let i = 0; i < s.networks.length; i++){
              list.push({id: s.id, name: s.name, network: s.networks[i]})
            }
          }
          else if ( s.networks.length === 1){
            list.push({id: s.id, name: s.name, network: s.networks[0]});
          }
          return list;
        }, []);

        // retrieving instance distribution across sites
        let instancePerSite = _.reduce(this.slices, (list, s) => {
          _.forEach(Object.keys(s.instance_distribution), k => {
            for(let i = 0; i < s.instance_distribution[k]; i++){
              list.push({site: k, instance: i})
            }
          })
          return list;
        }, []);

        this.sites = Object.keys(_.groupBy(instancePerSite, 'site'));

        this.instancePerSliceConfig.data = instances;
        this.instancePerSiteConfig.data = instancePerSite;
        this.networkPerSliceConfig.data = networkPerSlice;

      })
      .catch((e) => {
        throw new Error(e);
      });
    }
  };
});