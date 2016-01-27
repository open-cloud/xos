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

  var urlSuffix = '/rs/dashboard';

  function randomDate(start, end) {
    return new Date(
      start.getTime() + Math.random() * (end.getTime() - start.getTime())
    );
  }

  angular.module('cordHome', [])
    .controller('CordHomeCtrl', [
      '$log', '$scope', '$resource', '$filter', 'cordConfig', 'SubscriberUsers', 'Helpers',
      function ($log, $scope, $resource, $filter, cordConfig, SubscriberUsers, Helpers) {
        var DashboardData, resource;
        $scope.page.curr = 'dashboard';

        // NOTE subscriberId should be retrieved by login
        SubscriberUsers.query({subscriberId: 1}).$promise
        .then(function(res){
          $scope.bundle_name = cordConfig.bundles[0].name;
          $scope.bundle_desc = cordConfig.bundles[0].desc;

          // NOTE the loops creates data that are not available in xos should we move them in a service? Should we define a small backend to store this infos?

          // add an icon to the user
          res.users.map(function(user){
            user['icon_id'] = 'mom';
            return user;
          });

          // add a random login date to the user
          res.users.forEach(function(user){
            if(!angular.isDefined(cordConfig.userActivity[user.id])){
              var date = randomDate(new Date(2015, 0, 1), new Date());
              cordConfig.userActivity[user.id] = $filter('date')(date, 'mediumTime');
            }
          });
          $scope.users = res.users;
        })
        .catch(function(){
          $log.error('Problem with resource', resource);
        });

        $log.debug('Cord Home Ctrl has been created.');
      }]);
}());
