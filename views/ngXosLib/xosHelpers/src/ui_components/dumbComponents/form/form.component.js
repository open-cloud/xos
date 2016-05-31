/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 4/18/16.
 */

(function () {
  'use strict';

  angular.module('xos.uiComponents')

  /**
    * @ngdoc directive
    * @name xos.uiComponents.directive:xosForm
    * @restrict E
    * @description The xos-form directive.
    * This components have two usage, given a model it is able to autogenerate a form or it can be configured to create a custom form.
    * @param {Object} config The configuration object
    * ```
    * {
    *   exclude: ['id', 'validators', 'created', 'updated', 'deleted'], //field to be skipped in the form, the provide values are concatenated
    *   actions: [ // define the form buttons with related callback
    *     {
            label: 'save',
            icon: 'ok', // refers to bootstraps glyphicon
            cb: (user) => { // receive the model
              console.log(user);
            },
            class: 'success'
          }
    *   ],
    *   fields: {
    *     field_name: {
    *       label: 'Field Label',
    *       type: 'string' // options are: [date, boolean, number, email, string],
    *       validators: {
    *         minlength: number,
              maxlength: number,
              required: boolean,
              min: number,
              max: number
    *       }
    *     }
    *   }
    * }
    * ```
    * @element ANY
    * @scope
    * @requires xos.uiComponents.directive:xosField
    * @requires xos.uiComponents.XosFormHelpers
    * @requires xos.helpers._
    * @example
    
    Autogenerated form

  <example module="sampleForm">
    <file name="script.js">
      angular.module('sampleForm', ['xos.uiComponents'])
      .factory('_', function($window){
        return $window._;
      })
      .controller('SampleCtrl', function(){
        this.model = {
          first_name: 'Jhon',
          last_name: 'Doe',
          email: 'jhon.doe@sample.com',
          active: true,
          birthDate: '2015-02-17T22:06:38.059000Z'
        }
        this.config = {
          exclude: ['password', 'last_login'],
          formName: 'sampleForm',
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
      });
    </file>
    <file name="index.html">
      <div ng-controller="SampleCtrl as vm">
        <xos-form ng-model="vm.model" config="vm.config"></xos-form>
      </div>
    </file>
  </example>

  Configuration defined form

  <example module="sampleForm1">
    <file name="script.js">
      angular.module('sampleForm1', ['xos.uiComponents'])
      .factory('_', function($window){
        return $window._;
      })
      .controller('SampleCtrl1', function(){
        this.model = {
        };

        this.config = {
          exclude: ['password', 'last_login'],
          formName: 'sampleForm1',
          actions: [
            {
              label: 'Save',
              icon: 'ok', // refers to bootstraps glyphicon
              cb: (user) => { // receive the model
                console.log(user);
              },
              class: 'success'
            }
          ],
          fields: {
            first_name: {
              type: 'string',
              validators: {
                required: true
              }
            },
            last_name: {
              label: 'Surname',
              type: 'string',
              validators: {
                required: true,
                minlength: 10
              }
            },
            age: {
              type: 'number',
              validators: {
                required: true,
                min: 21
              }
            },
          }
        };
      });
    </file>
    <file name="index.html">
      <div ng-controller="SampleCtrl1 as vm">
        <xos-form ng-model="vm.model" config="vm.config"></xos-form>
      </div>
    </file>
  </example>

  **/

  .directive('xosForm', function(){
    return {
      restrict: 'E',
      scope: {
        config: '=',
        ngModel: '='
      },
      template: `
        <form name="vm.{{vm.config.formName || 'form'}}" novalidate>
          <div class="form-group" ng-repeat="(name, field) in vm.formField">
          <!--{{vm.ngModel[name] | json}}-->
            <xos-field name="name" field="field" ng-model="vm.ngModel[name]"></xos-field>
            <!--<pre>{{vm[vm.config.formName] || 'form'  | json }}</pre>-->
            <!--{{field}}-->
            <xos-validation field="vm[vm.config.formName || 'form'][name]" form = "vm[vm.config.formName || 'form']"></xos-validation>
            <div class="alert alert-info" ng-show="(field.hint).length >0" role="alert">{{field.hint}}</div>
          </div>
          <div class="form-group" ng-if="vm.config.actions">
            <button role="button" href=""
              ng-repeat="action in vm.config.actions"
              ng-click="action.cb(vm.ngModel)"
              class="btn btn-{{action.class}}"
              title="{{action.label}}">
              <i class="glyphicon glyphicon-{{action.icon}}"></i>
              {{action.label}}
            </button>
          </div>
        </form>
      `,
      bindToController: true,
      controllerAs: 'vm',
      controller: function($scope, $log, _, XosFormHelpers){

        if(!this.config){
          throw new Error('[xosForm] Please provide a configuration via the "config" attribute');
        }

        if(!this.config.actions){
          throw new Error('[xosForm] Please provide an action list in the configuration');
        }

        this.excludedField = ['id', 'validators', 'created', 'updated', 'deleted', 'backend_status'];
        if(this.config && this.config.exclude){
          this.excludedField = this.excludedField.concat(this.config.exclude);
        }


        this.formField = [];
        $scope.$watch(() => this.ngModel, (model) => {

          // empty from old stuff
          this.formField = {};

          if(!model){
            return;
          }

          let diff = _.difference(Object.keys(model), this.excludedField);
          let modelField = XosFormHelpers.parseModelField(diff);
          this.formField = XosFormHelpers.buildFormStructure(modelField, this.config.fields, model);
        });

      }
    }
  });
})();
