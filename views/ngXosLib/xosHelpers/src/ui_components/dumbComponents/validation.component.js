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
    */

  .directive('xosValidation', function(){
    return {
      restrict: 'E',
      scope: {
        errors: '='
      },
      template: `
        <div>
          <pre>{{vm.errors.email | json}}</pre>
          <xos-alert config="vm.config" show="vm.errors.email !== undefined">
            This is not a valid email
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
