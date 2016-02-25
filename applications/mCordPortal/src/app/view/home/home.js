/*
 * Copyright 2015 Open Networking Laboratory
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

(function () {
  'use strict';

  angular.module('cordHome', [])
    .controller('CordHomeCtrl', function ($log, $scope, $cookies, cordConfig, SubscriberUsers) {

      $scope.page.curr = 'dashboard';

      $scope.bundle_name = cordConfig.bundles[cordConfig.activeBundle].name;
      $scope.bundle_desc = cordConfig.bundles[cordConfig.activeBundle].desc;
      
      SubscriberUsers.query({subscriberId: $cookies.get('subscriberId')}).$promise
      .then(function(res){
        $scope.users = res;
      })
      .catch(function(){
        $log.error('Problem with resource', SubscriberUsers);
      });

      $log.debug('Cord Home Ctrl has been created.');
    });
}());
