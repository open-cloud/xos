'use strict';

angular.module('xos.tenant', [
  'ngResource',
  'ngCookies',
  'ui.router',
  'xos.helpers'
])
.config(($stateProvider) => {
  $stateProvider
  .state('site-list', {
    url: '/',
    template: '<site-list></site-list>'
  })
    .state('site', {
      url: '/site/:id',
      template: '<site-detail></site-detail>'

    })
    .state('createslice', {
      url: '/site/:site/slice/:id?',
      template: '<create-slice></create-slice>'

    });
})
.config(function($httpProvider){
  $httpProvider.interceptors.push('NoHyperlinks');
})
.directive('siteList', function(){
  return {
    //sites : {},
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/users-list.tpl.html',
    controller: function(Sites, SlicesPlus){



      this.tableConfig = {
        columns: [
          {
            label: 'Site',
            prop: 'name',
            link: item => `#/site/${item.id}`
          },
          {
            label: 'Allocated',
            prop: 'instance_total'
          },
          {
            label: 'Ready',
            prop: 'instance_total_ready'
          }
        ]
      };

      // retrieving user list
      Sites.query().$promise
      .then((users) => {
        this.sites = users;
        return  SlicesPlus.query().$promise
      })
      .then((users) => {
        this.slices = users;
        this.site_list = this.returnData(this.sites, this.slices);
      })
      .catch((e) => {
        throw new Error(e);
      });


      this.returnData = (sites, slices) => {
        var i, j=0;
        var site_list=[];

        for(i = 0; i<sites.length; i++){
          var instance_t = 0;
          var instance_t_r = 0;
          for(j=0;j<slices.length;j++){
            if (sites[i].id != null && slices[j].site !=null && sites[i].id === slices[j].site){
              instance_t = instance_t + slices[j].instance_total;
              instance_t_r = instance_t_r + slices[j].instance_total_ready;
            }
          }
          var data_sites = {
            'id': sites[i].id,
            'name': sites[i].name,
            'instance_total': instance_t,
            'instance_total_ready': instance_t_r
          };
          site_list.push(data_sites);
        }
        return site_list;
      }
    }
  };
});
