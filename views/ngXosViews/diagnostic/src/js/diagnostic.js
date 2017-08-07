
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
  .directive('diagnosticContainer', function(){
    return {
      restrict: 'E',
      templateUrl: 'templates/diagnostic.tpl.html',
      controllerAs: 'vm',
      controller: function(ChartData, Subscribers, SubscribersWithDevice, ServiceRelation, $rootScope){

        this.loader = true;
        this.error = false;
        
        const loadGlobalScope = () => {
          Subscribers.query().$promise
          .then((subscribers) => {
            this.subscribers = subscribers;
            return ServiceRelation.get();
          })
          .then((serviceChain) => {
            this.serviceChain = serviceChain;
            // debug helper
            // loadSubscriber(this.subscribers[0]);
          })
          .catch(e => {
            throw new Error(e);
            this.error = e;
          })
          .finally(() => {
            this.loader = false;
          });
        };

        loadGlobalScope();

        this.reloadGlobalScope = () => {
          this.selectedSubscriber = null;
          loadGlobalScope();
        }

        const loadSubscriber = (subscriber) => {
          ServiceRelation.getBySubscriber(subscriber)
          .then((serviceChain) => {
            this.serviceChain = serviceChain;
            ChartData.currentServiceChain = serviceChain;
            return SubscribersWithDevice.get({id: subscriber.id}).$promise;
          })
          .then((subscriber) => {
            this.selectedSubscriber = subscriber;
            ChartData.currentSubscriber = subscriber;
          });
        };

        $rootScope.$on('subscriber.selected', (evt, subscriber) => {
          loadSubscriber(subscriber);
        });

      }
    }
  });
})();
