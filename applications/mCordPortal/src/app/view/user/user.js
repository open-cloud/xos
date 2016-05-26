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

  angular.module('cordUser', [])
    .controller('CordUserCtrl', function ($log, $scope, $resource, $timeout, $filter, $cookies, SubscriberUsers, cordConfig, SubscriberUsersUrlFilterLevel) {

      $scope.page.curr = 'user';
      $scope.isFamily = false;
      $scope.newLevels = {};
      $scope.showCheck = false;
      $scope.ratingsShown = false;
      
      SubscriberUsers.query({subscriberId: $cookies.get('subscriberId')}).$promise
        .then(function(res){
          $scope.isFamily = cordConfig.bundles[cordConfig.activeBundle].id === 'family';
          // if bundle is family search for url_filter level
          if ($scope.isFamily) {
            angular.forEach(cordConfig.bundles[cordConfig.activeBundle].functions, function(fn){
              if(fn.id === 'video'){
                console.log(fn);
                $scope.levels = fn.params.levels;
              }
            });
          }
          $scope.users = res;
        })
        .catch(function () {
          $log.error('Problem with resource', SubscriberUsers);
        });

      $scope.updateLevel = function(user){
        // TODO save this data and show a confirmation to the user
        // NOTE subscriberId should be retrieved by login
        SubscriberUsersUrlFilterLevel.updateUrlFilterLevel(1, user.id, user.level)
          .then(function(){
            user.updated = true;
          })
          .catch(function(e){
            throw new Error(e);
          });
      };

      $scope.showRatings = function () {
        $scope.ratingsShown = !$scope.ratingsShown;
      };

      $log.debug('Cord User Ctrl has been created.');
    })
    .directive('userUpdatedTick', function($timeout){
      return {
        restric: 'E',
        scope: {
          user: '='
        },
        template: '<span class="icon-saved animate" ng-show="saved"></span>',
        link: function(scope, elem){
          scope.saved = false;
          scope.$watch('user.updated', function(val){
            if(val){
              scope.saved = true;
              $timeout(function(){
                scope.saved = false;
              }, 3000);
            }
          });
        }
      }
    });
}());
