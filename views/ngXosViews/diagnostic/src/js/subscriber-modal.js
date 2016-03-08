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
      controller: function($log, $timeout, $scope, Subscribers){

        $scope.$watch(() => this.open, () => {
          this.success = null;
          this.formError = null;
        });

        $scope.$watch(() => this.subscriber, () => {
          this.subscriber.uplink_speed = parseInt(this.subscriber.uplink_speed, 10);
          this.subscriber.downlink_speed = parseInt(this.subscriber.downlink_speed, 10);
        });

        this.close = () => {
          this.open = false;
        };

        this.updateSubscriber = (subscriber) => {

          Subscribers.update(subscriber).$promise
          .then(() => {
            this.success = 'Subscriber successfully updated!';
          })
          .catch((e) => {
            this.formError = e;
          })
          .finally(() => {
            $timeout(() => {
              this.close();
            }, 1500);
          });
        };
      }
    };
  });
})();
