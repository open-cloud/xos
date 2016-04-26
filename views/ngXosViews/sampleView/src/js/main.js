'use strict';

angular.module('xos.sampleView', [
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
  });
})
.config(function($httpProvider){
  $httpProvider.interceptors.push('NoHyperlinks');
})
.directive('usersList', function(){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/users-list.tpl.html',
    controller: function(Users, _){

      this.tableConfig = {
        columns: [
          {
            label: 'E-Mail',
            prop: 'email'
          },
          {
            label: 'First Name',
            prop: 'firstname'
          },
          {
            label: 'Last Name',
            prop: 'lastname'
          }
        ],
        classes: 'table table-striped table-condensed',
        actions: [
          {
            label: 'delete',
            icon: 'remove',
            cb: (user) => {
              console.log(user);
              // _.remove(this.users, {id: user.id});
            },
            color: 'red'
          }
        ],
        filter: 'field',
        order: true,
        pagination: {
          pageSize: 10
        }
      };

      this.smartTableConfig = {
        resource: 'Users',
        hiddenFields: [
          'email',
          'username',
          'created',
          'updated',
          'last_login',
          'is_active',
          'is_admin',
          'is_staff',
          'is_readonly',
          'is_registering',
          'is_appuser'
        ]
      }

      this.alertConfig = {
        type: 'danger',
        closeBtn: true
      }

      this.formConfig = {
        exclude: ['password'],
        formName: 'myForm',
        fields: {
          firstname: {
            validators: {
              minlength: 10
            }
          },
          lastname: {
            validators: {
              maxlength: 3
            }
          },
          user_url: {
            validators: {
              required: true
            }
          }
        },
        actions: [
          {
            label: 'Save',
            icon: 'ok', // refers to bootstraps glyphicon
            cb: (user) => { // receive the model
              console.log(user);
            },
            class: 'success'
          }
        ]
      };

      this.errors = {
        email: false
      }

      // retrieving user list
      Users.query().$promise
      .then((users) => {
        this.users = users.concat(users).concat(users).concat(users);
      })
      .catch((e) => {
        throw new Error(e);
      });
    }
  };
});