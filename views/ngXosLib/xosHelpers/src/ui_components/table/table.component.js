/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 3/24/16.
 */

(function () {
  'use strict';

  angular.module('xos.uiComponents.table', [])
    .directive('xosTable', function(){
      return {
        restrict: 'E',
        scope: {
          data: '=',
          columns: '='
        },
        bindToController: true,
        controllerAs: 'vm',
        controller: function(){
          console.log(this.data, this.columns);
        }
      }
    })
})();
