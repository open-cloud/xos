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

        const mb = 1000000;

        $scope.$watch(() => this.open, () => {
          this.success = null;
          this.formError = null;
        });

        $scope.$watch(() => this.subscriber, (newVal, oldVal) => {
          if(!this.subscriber){
            return;
          }
          console.log(newVal, oldVal);
          console.log('subscriber change', newVal === oldVal);
          this.subscriber.uplink_speed = parseInt(this.subscriber.uplink_speed, 10) / mb;
          this.subscriber.downlink_speed = parseInt(this.subscriber.downlink_speed, 10) / mb;
        });

        this.close = () => {
          this.open = false;
        };

        this.updateSubscriber = (subscriber) => {

          // TODO Copy the subscriber, this will update the GUI also and we don't want
          // TODO Change GBps to MBps

          let body = angular.copy(subscriber, body);

          body.uplink_speed = body.uplink_speed * mb;
          body.downlink_speed = body.downlink_speed * mb;

          Subscribers.update(body).$promise
          .then((res) => {
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
