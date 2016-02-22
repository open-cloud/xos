(function () {
  'use strict';

  angular.module('xos.serviceTopology')
  .directive('diagnostic', function(){
    return {
      restrict: 'E',
      templateUrl: 'templates/diagnostic.tpl.html',
      controllerAs: 'vm',
      controller: function(Subscribers, ServiceRelation){
        this.loader = true;
        this.error = false;
        Subscribers.query().$promise
        .then((subscribers) => {
          this.subscribers = subscribers;
          return ServiceRelation.get();
        })
        .then((serviceChain) => {
          this.serviceChain = serviceChain;
        })
        .catch(e => {
          throw new Error(e);
          this.error = e;
        })
        .finally(() => {
          this.loader = false;
        });
      }
    }
  });
})();