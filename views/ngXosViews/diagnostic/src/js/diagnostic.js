(function () {
  'use strict';
  angular.module('xos.diagnostic')
  .directive('diagnosticContainer', function(){
    return {
      restrict: 'E',
      templateUrl: 'templates/diagnostic.tpl.html',
      controllerAs: 'vm',
      controller: function(ChartData, Subscribers, ServiceRelation, $rootScope, $log){

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

        $rootScope.$on('subscriber.selected', (evt, subscriber) => {
          ServiceRelation.getBySubscriber(subscriber)
          .then((serviceChain) => {
            this.serviceChain = serviceChain;
            ChartData.currentServiceChain = serviceChain;
            return Subscribers.getWithDevices({id: subscriber.id}).$promise;
          })
          .then((subscriber) => {
            this.selectedSubscriber = subscriber;
            ChartData.currentSubscriber = subscriber;
          });
        });
      }
    }
  });
})(); 