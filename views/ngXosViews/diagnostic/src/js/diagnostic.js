(function () {
  'use strict';

  angular.module('xos.serviceTopology')
  .directive('diagnostic', function(){
    return {
      restrict: 'E',
      templateUrl: 'templates/diagnostic.tpl.html',
      controllerAs: 'vm',
      controller: function(Subscribers, ServiceRelation){
        Subscribers.queryWithDevices().$promise
        .then((subscribers) => {
          console.log(subscribers);
          this.subscribers = subscribers;
          return ServiceRelation.get(subscribers[0]);
        })
        .then((serviceChain) => {
          this.serviceChain = serviceChain;
        });
      }
    }
  });
})();