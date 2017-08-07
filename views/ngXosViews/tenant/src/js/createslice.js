
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


/**
 * Created by arpit on 7/7/2016.
 */
'use strict';

angular.module('xos.tenant')
.directive('createSlice', function(){
  return {
    //sites : {},
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'cs',
    templateUrl: 'templates/createslice.html',
    controller: function(Slices, SlicesPlus, Sites, Images, $stateParams, $http, $state, $q, XosUserPrefs,_){
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
              saveform(model, form);
            },
            class: 'primary'
          },
          {
            label: 'Save and add another',
            icon: 'ok', // refers to bootstraps glyphicon
            cb: (model, form) => {
              saveform(model, form).then(()=> {
                $state.go('createslice', { site: this.model.site, id: ''});
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
              required: true,
              custom: (value)=>{
                if(this.model.site){
                  var selectVal = _.find(this.config.fields.site.options,['id',this.model.site]);
                  if(selectVal && value){
                    return (value.toLowerCase().indexOf(selectVal.label.toLowerCase()) === 0);
                  }
                }
                return false;
              }
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
        XosUserPrefs.getUserDetailsCookie().$promise
        .then((userdata)=>{
          this.model['creator'] =userdata.current_user_id;
        })
        .catch ((e) => {
          throw new Error(e);
        });

        Sites.query().$promise
        .then((users) => {
          this.users_site = users;
          this.optionVal = this.setData(this.users_site, {field1: 'id', field2: 'name'});
          this.config.fields['site'].options = this.optionVal;
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
            this.config.feedback.show = true;
            deferred.resolve(users);
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