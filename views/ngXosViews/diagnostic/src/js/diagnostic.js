(function () {
  'use strict';

  angular.module('xos.serviceTopology')
  .directive('diagnostic', function(){
    return {
      restrict: 'E',
      templateUrl: 'templates/diagnostic.tpl.html',
      controllerAs: 'vm',
      controller: function(Subscribers, ServiceRelation){
        Subscribers.query().$promise
        .then((subscribers) => {
          this.subscribers = subscribers;
          this.selectedSubscriber = subscribers[0];
          return ServiceRelation.get(this.selectedSubscriber);
        })
        .then((serviceChain) => {
          this.serviceChain = serviceChain;
        });
      }
    }
  });
})();