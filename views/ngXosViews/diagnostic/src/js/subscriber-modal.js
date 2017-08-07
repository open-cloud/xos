
/*
 * Copyright 2017-present Open Networking Foundation

 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at

 * http://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


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
          this.subscriber.features.uplink_speed = parseInt(this.subscriber.features.uplink_speed, 10) / mb;
          this.subscriber.features.downlink_speed = parseInt(this.subscriber.features.downlink_speed, 10) / mb;
        });

        this.close = () => {
          this.open = false;
        };

        this.updateSubscriber = (subscriber) => {

          // TODO Copy the subscriber, this will update the GUI also and we don't want
          // TODO Change GBps to MBps

          let body = angular.copy(subscriber, body);

          body.features.uplink_speed = body.features.uplink_speed * mb;
          body.features.downlink_speed = body.features.downlink_speed * mb;

          // remove read only attributes
          delete body.related;

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
