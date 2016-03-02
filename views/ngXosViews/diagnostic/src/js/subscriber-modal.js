(function () {
  'use strict';
  angular.module('xos.diagnostic')
  .directive('selectSubscriberModal', function(){
    return {
      scope: {
        subscribers: '=',
        open: '='
      },
      bindToController: true,
      restrict: 'E',
      templateUrl: 'templates/select-subscriber-modal.tpl.html',
      controllerAs: 'vm',
      controller: function($rootScope){

        this.close = () => {
          this.open = false;
        };

        this.select = (subscriber) => {
          $rootScope.$emit('subscriber.selected', subscriber);
          this.close();
        };
      }
    };
  })
  .directive('subscriberStatusModal', function(){
    return {
      scope: {
        open: '=',
        subscriber: '='
      },
      bindToController: true,
      restrict: 'E',
      templateUrl: 'templates/subscriber-status-modal.tpl.html',
      controllerAs: 'vm',
      controller: function($log, $scope){

        // mock until api
        $scope.$watch(() => this.subscriber, (subscriber) => {
          if(subscriber){
            subscriber.status = 'enabled';
          }
        });

        this.close = () => {
          this.open = false;
        };

        this.setStatus = (status) => {
          this.subscriber.status = status;
          $log.info(`Set subscriber status to: ${status}`);
        };
      }
    };
  });
})();
