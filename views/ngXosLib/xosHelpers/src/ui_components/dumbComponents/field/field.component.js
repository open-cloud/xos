/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 5/25/16.
 */

(function () {
  'use strict';

  angular.module('xos.uiComponents')
  /**
    * @ngdoc directive
    * @name xos.uiComponents.directive:xosField
    * @restrict E
    * @description The xos-field directive.
    * This component decide, give a field wich kind of input it need to print.
    * @param {string} name The field name
    * @param {object} field The field configuration:
    * ```
    * {
    *   label: 'Label',
    *   type: 'number', //typeof field
    *   validators: {} // see xosForm for more details
    * }
    * ```
    * @param {mixed} ngModel The field value
    */
  .directive('xosField', function(){
    return {
      restrict: 'E',
      scope: {
        name: '=',
        field: '=',
        ngModel: '='
      },
      template: `
        <label>{{vm.field.label}}</label>
            <input
              ng-if="vm.field.type !== 'boolean' && vm.field.type !== 'object'"
              type="{{vm.field.type}}"
              name="{{vm.name}}"
              class="form-control"
              ng-model="vm.ngModel"
              ng-minlength="vm.field.validators.minlength || 0"
              ng-maxlength="vm.field.validators.maxlength || 2000"
              ng-required="vm.field.validators.required || false" />
            <span class="boolean-field" ng-if="vm.field.type === 'boolean'">
              <button
                class="btn btn-success"
                ng-show="vm.ngModel"
                ng-click="vm.ngModel = false">
                <i class="glyphicon glyphicon-ok"></i>
              </button>
              <button
                class="btn btn-danger"
                ng-show="!vm.ngModel"
                ng-click="vm.ngModel = true">
                <i class="glyphicon glyphicon-remove"></i>
              </button>
            </span>
            <div
              class="panel panel-default object-field"
              ng-if="vm.field.type == 'object' "
              >
              <div class="panel-heading">Panel heading without title</div>
              <div class="panel-body">
                Panel content
              </div>
            </div>
      `,
      bindToController: true,
      controllerAs: 'vm',
      controller: function(){
        // console.log('Field: ', this.name, this.field.type, this.ngModel);
        if(!this.name){
          throw new Error('[xosField] Please provide a field name');
        }
        if(!this.field){
          throw new Error('[xosField] Please provide a field definition');
        }
        if(!this.ngModel){
          throw new Error('[xosField] Please provide an ng-model');
        }
      }
    }
  });
})();