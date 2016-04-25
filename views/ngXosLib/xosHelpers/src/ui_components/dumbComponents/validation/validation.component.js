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
        errors: '='
      },
      template: `
        <div ng-cloak>
          <!-- <pre>{{vm.errors.email | json}}</pre> -->
          <xos-alert config="vm.config" show="vm.errors.required !== undefined && vm.errors.required !== false">
            Field required
          </xos-alert>
          <xos-alert config="vm.config" show="vm.errors.email !== undefined && vm.errors.email !== false">
            This is not a valid email
          </xos-alert>
          <xos-alert config="vm.config" show="vm.errors.minlength !== undefined && vm.errors.minlength !== false">
            Too short
          </xos-alert>
          <xos-alert config="vm.config" show="vm.errors.maxlength !== undefined && vm.errors.maxlength !== false">
            Too long
          </xos-alert>
          <xos-alert config="vm.config" show="vm.errors.custom !== undefined && vm.errors.custom !== false">
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
