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
})
.directive('siteDetail', function(){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'sl',
    templateUrl: 'templates/slicelist.html',
    controller: function(SlicesPlus, $stateParams){
      this.siteId  = $stateParams.id;
      this.tableConfig = {
        columns: [
          {
            label: 'Slice List',
            prop: 'name',
            link: item => `#/site/${item.site}/slice/${item.id}`
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
        this.sliceList = users;
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
    controller: function(Slices, SlicesPlus, Sites, Images, $stateParams, $http, $state, $q){
      this.config = {
        exclude: ['site', 'password', 'last_login', 'mount_data_sets', 'default_flavor', 'creator', 'exposed_ports', 'networks', 'omf_friendly', 'omf_friendly', 'no_sync', 'no_policy', 'lazy_blocked', 'write_protect', 'deleted', 'backend_status', 'backend_register', 'policed', 'enacted', 'updated', 'created', 'validators', 'humanReadableName'],
        formName: 'SliceDetails',
        feedback: {
          show: false,
          message: 'Form submitted successfully !!!',
          type: 'success'
        },
        actions: [
          {
            label: 'Save',
            icon: 'ok', // refers to bootstraps glyphicon
            cb: (model, form) => { // receive the model
              saveform(model, form).then(()=> {
                $state.go('site', {id: this.model.site});
              });
            },
            class: 'success'
          },  {
            label: 'Save and continue editing',
            icon: 'ok', // refers to bootstraps glyphicon
            cb: (model, form) => { // receive the model
              saveform(model,form);
            },
            class: 'primary'
          },
          {
            label: 'Save and add another',
            icon: 'ok', // refers to bootstraps glyphicon
            cb: (model, form) => {
              saveform(model,form).then(()=> {
                $state.go('createslice',{site : this.model.site,id : ''});
              });
            },
            class: 'primary'
          }
        ],
        fields:
        {
          site: {
            label: 'Site',
            type: 'select',
            validators: { required: true},
            hint: 'The Site this Slice belongs to',
            options: []

          },
          name: {
            label: 'Name',
            type: 'string',
            hint: 'The Name of the Slice',
            validators: {
              required: true
            }
          },
          serviceClass: {
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
            label: 'Max Instances',
            type: 'number',
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
            options: []
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
      Images.query().$promise
          .then((users) => {
            this.users = users;
            data = this.users;
            this.optionValImg = this.setData(data, {field1: 'id', field2: 'name'});
            this.config.fields['default_image'].options = this.optionValImg;
          })
          .catch((e) => {
            throw new Error(e);
          });

      // Use this method for select by seting object in fields variable of format { field1 : "val1", field2 : "val2"}
      this.setData = (data, fields) => {
        var i;
        var retObj=[];
        for(i = 0; i<data.length; i++){
          var optVal = {id: data[i][fields.field1], label: data[i][fields.field2]};
          retObj.push(optVal);

        }
        return retObj;
      };

      // retrieving user list

      if ($stateParams.id)
      {
        delete this.config.fields['site'];
        this.config.exclude.push('site');

        Slices.get({id: $stateParams.id}).$promise
          .then((users) => {
            this.users = users;
            data = users;

            this.model = data;
          })
          .catch((e) => {
            throw new Error(e);
          });
      }
      else
      {


        this.model = {};
        $http.get('/xoslib/tenantview/').
        success((data) => {
          this.userList = data;
          this.model['creator'] = this.userList.current_user_id;

        });






        Sites.query().$promise
      .then((users) => {
        this.users_site = users;
        this.optionVal = this.setData(this.users_site, {field1: 'id', field2: 'name'});
        this.config.fields['site'].options = this.optionVal;
        //= this.optionVal;

      })
      .catch((e) => {
        throw new Error(e);
      });

      }

      var  saveform = (model,form) =>
      { // receive the model
        var deferred = $q.defer();
        delete model.networks;
        if (form.$valid )
        {
          if(model.id){
            var pr = Slices.update(model).$promise;
          }
          else{
            var pr = Slices.save(model).$promise;
          }
          pr.then((users) => {
            this.model = users;
            //data = users;
            //this.model = this.users;
            this.config.feedback.show = true;
            deferred.resolve(this.model);
          })
          .catch((e) => {
            this.config.feedback.show = true;
            this.config.feedback.type='danger';
            if(e.data && e.data.detail )
            {
              this.config.feedback.message = e.data.detail;
            }
            else {
              this.config.feedback.message=e.statusText;
            }
            deferred.reject(e);
          });
        }

        return  deferred.promise;
      }
    }
  };
});