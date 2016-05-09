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
    controller: function($scope, $timeout, SlicesPlus, _){

      this.instancePerSliceConfig = {
        resource: 'Instances',
        groupBy: 'slice',
        legend: true,
        labelFormatter: (labels) => {
          return labels.map(l => _.find(this.slices, {id: parseInt(l)}).name);
        }
      };

      this.instancePerSiteConfig = {
        data: [],
        groupBy: 'site',
        legend: true,
      };

      this.networkPerSliceConfig = {
        data: [],
        groupBy: 'name',
        legend: true,
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
            label: 'Sites',
            type: 'object',
            prop: 'instance_distribution'
            // formatter: item => item.instance_distribution
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
      .then(slices => {
        
        // retrieving network per slices
        let networkPerSlice = _.reduce(slices, (list, s) => {
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
        let instancePerSite = _.reduce(slices, (list, s) => {
          _.forEach(Object.keys(s.instance_distribution), k => {
            for(let i = 0; i < s.instance_distribution[k]; i++){
              list.push({site: k, instance: i})
            }
          })
          return list;
        }, []);

        $timeout(() => {
          console.log(instancePerSite, networkPerSlice);
          this.instancePerSiteConfig.data = instancePerSite;
          this.networkPerSliceConfig.data = networkPerSlice;
          $scope.$apply();
        }, 1);

        this.slices = slices;
      })
      .catch((e) => {
        throw new Error(e);
      });
    }
  };
});