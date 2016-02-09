(function () {
  'use strict';
  angular.module('xos.serviceTopology')
  .directive('logicTopology', function(){
    return {
      restrict: 'E',
      scope: {
        serviceChain: '='
      },
      bindToController: true,
      controllerAs: 'vm',
      template: '',
      controller: function($element, $log){
        $log.info('Logic Plane');

        
      }
    };
  });
})();
