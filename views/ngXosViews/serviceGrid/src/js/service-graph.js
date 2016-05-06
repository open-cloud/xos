(function () {
  'use strict';

  angular.module('xos.serviceGrid')
  .directive('serviceGraph', function(){
    return {
      restrict: 'E',
      scope: {},
      bindToController: true,
      controllerAs: 'vm',
      templateUrl: 'templates/service-graph.tpl.html',
      controller: function(){

      }
    };
  })
})();