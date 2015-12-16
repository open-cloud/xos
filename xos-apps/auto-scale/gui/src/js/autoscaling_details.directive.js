angular.module('autoscaling')
.directive('serviceContainer', function(lodash){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/service-container.tpl.html',
    controller: ($rootScope) => {
      $rootScope.$on('autoscaling.update', (evt, data) => {
        console.log(data);
      });
    }
  };
});
