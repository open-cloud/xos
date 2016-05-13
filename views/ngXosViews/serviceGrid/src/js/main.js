'use strict';

angular.module('xos.serviceGrid', [
  'ngResource',
  'ngCookies',
  'ui.router',
  'xos.helpers'
])
.config(($stateProvider) => {
  $stateProvider
  .state('serviceGrid', {
    url: '/',
    template: '<service-grid></service-grid>'
  })
  .state('serviceGraph', {
    url: '/graph',
    template: '<service-graph></service-graph>'
  });
})
.config(function($httpProvider){
  $httpProvider.interceptors.push('NoHyperlinks');
})
.directive('serviceGrid', function(){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/service-grid.tpl.html',
    controller: function(Services, _){

      this.tableConfig = {
        columns: [
          {
            label: 'Status',
            prop: 'status',
            type: 'boolean',
          },
          {
            label: 'Name',
            prop: 'name',
            link: item => `${item.view_url.replace(/\$[a-z]+\$/, item.id)}`
          },
          {
            label: 'Kind',
            prop: 'kind'
          },
          {
            label: 'Enabled',
            prop: 'enabled',
            type: 'boolean'
          }
        ],
        filter: 'field',
        order: true
      };
      
      // retrieving user list
      Services.query().$promise
      .then((services) => {
        this.services = _.map(services, s => {
          // parse backend_status string in a boolean for display
          // NOTE they are not boolean:
          // - start with 0 = provisioning
          // - start with 1 = good
          // - start with 2 = error
          s.status = parseInt(s.backend_status.match(/^[0-9]/)[0]) === 0 ? false : true;
          return s;
        })
      })
      .catch((e) => {
        throw new Error(e);
      });
    }
  };
});