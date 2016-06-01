/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 4/15/16.
 */

(function () {
  'use strict';

  angular.module('xos.uiComponents')

  /**
    * @ngdoc directive
    * @name xos.uiComponents.directive:xosValidation
    * @restrict E
    * @description The xos-validation directive
    * @param {Object} errors The error object
    * @element ANY
    * @scope
  * @example
  <example module="sampleValidation">
    <file name="index.html">
      <div ng-controller="SampleCtrl as vm">
        <div class="row">
          <div class="col-xs-12">
            <label>Set an error type:</label>
          </div>
          <div class="col-xs-2">
            <a class="btn"
              ng-click="vm.errors.required = !vm.errors.required"
              ng-class="{'btn-default': !vm.errors.required, 'btn-success': vm.errors.required}">
              Required
            </a>
          </div>
          <div class="col-xs-2">
            <a class="btn"
              ng-click="vm.errors.email = !vm.errors.email"
              ng-class="{'btn-default': !vm.errors.email, 'btn-success': vm.errors.email}">
              Email
            </a>
          </div>
          <div class="col-xs-2">
            <a class="btn"
              ng-click="vm.errors.minlength = !vm.errors.minlength"
              ng-class="{'btn-default': !vm.errors.minlength, 'btn-success': vm.errors.minlength}">
              Min Length
            </a>
          </div>
          <div class="col-xs-2">
            <a class="btn"
              ng-click="vm.errors.maxlength = !vm.errors.maxlength"
              ng-class="{'btn-default': !vm.errors.maxlength, 'btn-success': vm.errors.maxlength}">
              Max Length
            </a>
          </div>
        </div>
        <xos-validation errors="vm.errors"></xos-validation>
      </div>
    </file>
    <file name="script.js">
      angular.module('sampleValidation', ['xos.uiComponents'])
      .controller('SampleCtrl', function(){
        this.errors = {
          email: false
        }
      });
    </file>
  </example>
    */

  .directive('xosValidation', function(){
    return {
      restrict: 'E',
      scope: {
        field: '=',
        form: '='
      },
      template: `
        <div ng-cloak>
          <xos-alert config="vm.config" show="vm.field.$error.required !== undefined && vm.field.$error.required !== false  && (vm.field.$touched || vm.form.$submitted)">
            Field required
          </xos-alert>
          <xos-alert config="vm.config" show="vm.field.$error.email !== undefined && vm.field.$error.email !== false  && (vm.field.$touched || vm.form.$submitted)">
            This is not a valid email
          </xos-alert>
          <xos-alert config="vm.config" show="vm.field.$error.minlength !== undefined && vm.field.$error.minlength !== false  && (vm.field.$touched || vm.form.$submitted)">
            Too short
          </xos-alert>
          <xos-alert config="vm.config" show="vm.field.$error.maxlength !== undefined && vm.field.$error.maxlength !== false  && (vm.field.$touched || vm.form.$submitted)">
            Too long
          </xos-alert>
          <xos-alert config="vm.config" show="vm.field.$error.custom !== undefined && vm.field.$error.custom !== false  && (vm.field.$touched || vm.form.$submitted)">
            Field invalid
          </xos-alert>
        </div>
      `,
      transclude: true,
      bindToController: true,
      controllerAs: 'vm',
      controller: function(){
        this.config = {
          type: 'danger'
        }
      }
    }
  })
})();
