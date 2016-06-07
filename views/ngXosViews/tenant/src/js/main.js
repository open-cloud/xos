'use strict';

angular.module('xos.tenant', [
  'ngResource',
  'ngCookies',
  'ui.router',
  'xos.helpers'
])
.config(($stateProvider) => {
  $stateProvider
  .state('user-list', {
    url: '/',
    template: '<users-list></users-list>'
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
.directive('usersList', function(){
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
            label: 'Site1',
            prop: 'name',
            link: item => `/#/site/${item.id}`
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
        //console.log(this.sites,this.slices);
        this.site_list = this.returnData(this.sites, this.slices);
      })
      .catch((e) => {
        throw new Error(e);
      });


      this.returnData = (sites, slices) => {
        //console.log(sites,slices);
        //console.log(sites.length)
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
          //console.log(sites[i].id);
          site_list.push(data_sites);
        }
        return site_list;
        //this.site_list = site_list;
      }
    }
  };
})
.directive('siteDetail', function(){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'sl',
    templateUrl: 'templates/slicelist.html',
    controller: function(SlicesPlus, $stateParams){
      this.tableConfig = {
        columns: [
          {
            label: 'Slice List',
            prop: 'name',
            link: item => `/#/site/${item.site}/slice/${item.id}`
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
      SlicesPlus.query({
        site: $stateParams.id
      }).$promise
      .then((users) => {
        this.users = users;
      })
      .catch((e) => {
        throw new Error(e);
      });
    }
  };
})
.directive('createSlice', function(){
  return {
    //sites : {},
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'cs',
    templateUrl: 'templates/createslice.html',
    controller: function(Slices, SlicesPlus, $stateParams){
      //var sites;
      //console.log(this.users.name);

      //console.log(this.config);
      this.config = {
        exclude: ['password', 'last_login'],
        formName: 'SliceDetails',
        actions: [
          {
            label: 'Save',
            icon: 'ok', // refers to bootstraps glyphicon
            cb: (user) => { // receive the model
              console.log(user);
            },
            class: 'success'
          },  {
            label: 'Save and continue editing',
            icon: 'ok', // refers to bootstraps glyphicon
            cb: (user) => { // receive the model
              console.log(user);
            },
            class: 'primary'
          },
          {
            label: 'Save and add another',
            icon: 'ok', // refers to bootstraps glyphicon
            cb: (user) => { // receive the model
              console.log(user);
            },
            class: 'primary'
          }
        ],
        fields:
        {
          site_select: {
            label: 'Site',
            type: 'select',
            validators: { required: true},
            hint: 'The Site this Slice belongs to',
            options: [
              {
                id: 0,
                label: '---Site---'
              },
              {
                id: 1,
                label: '---Site1---'
              }]

          },
          first_name: {
            label: 'Name',
            type: 'string',
            hint: 'The Name of the Slice',
            validators: {
              required: true
            }
          },
          service_class: {
            label: 'ServiceClass',
            type: 'select',
            validators: {required: true},
            hint: 'The Site this Slice belongs to',
            options: [
              {
                id: 1,
                label: 'Best effort'
              }
            ]
          },
          enabled: {
            label: 'Enabled',
            type: 'boolean',
            hint: 'Status for this Slice'
          },
          description: {
            label: 'Description',
            type: 'string',
            hint: 'High level description of the slice and expected activities',
            validators: {
              required: false,
              minlength: 10
            }
          },
          service: {
            label: 'Service',
            type: 'select',
            validators: { required: false},
            options: [
              {
                id: 0,
                label: '--------'
              }
            ]
          },
          slice_url: {
            label: 'Slice url',
            type: 'string',
            validators: {
              required: false,
              minlength: 10
            }
          },
          max_instances: {
            type: 'Max Instances',
            validators: {
              required: false,
              min: 0
            }
          },
          default_isolation: {
            label: 'Default Isolation',
            type: 'select',
            validators: { required: false},
            options: [
              {
                id: 'vm',
                label: 'Virtual Machine'
              },
              {
                id: 'container',
                label: 'Container'
              },
              {
                id: 'container_vm',
                label: 'Container in VM'
              }
            ]
          },
          default_image: {
            label: 'Default image',
            type: 'select',
            validators: { required: false},
            options: [
              {
                id: 0,
                label: 'trusty-server-multi-nic'
              }
            ]
          },
          network: {
            label: 'Network',
            type: 'select',
            validators: { required: false},
            options: [
              {
                id: 'default',
                label: 'Default'
              },
              {
                id: 'host',
                label: 'Host'
              },
              {
                id: 'bridged',
                label: 'Bridged'
              },
              {
                id: 'noauto',
                label: 'No Automatic Networks'
              }
            ]
          }

        }
      };

      var data;
      // retrieving user list
      if ($stateParams.id)
      {
        Slices.get({id: $stateParams.id}).$promise
          .then((users) => {
            this.users = users;
            data = users;
            this.model = {
              first_name: data.name,
              service_class: data.serviceClass,
              enabled: data.enabled,
              description: data.description,
              service: data.service,
              slice_url: data.slice_url,
              max_instances: data.max_instances,
              default_isolation: data.default_isolation,
              default_image: data.default_image,
              network: data.network
            };
          })
          .catch((e) => {
            throw new Error(e);
          });
      }
      else
      {
        this.model = {};
      }
    }
  };
});