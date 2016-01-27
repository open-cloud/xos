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
    .controller('CordUserCtrl', function ($log, $scope, $resource, $timeout, $filter, SubscriberUsers, cordConfig) {

      $scope.page.curr = 'user';
      $scope.isFamily = false;
      $scope.newLevels = {};
      $scope.showCheck = false;
      $scope.ratingsShown = false;

      // NOTE subscriberId should be retrieved by login
      SubscriberUsers.query({subscriberId: 1}).$promise
        .then(function(res){
          $scope.isFamily = cordConfig.bundles[cordConfig.activeBundle].id === 'family';
          // if bundle is family search for url_filter level
          if ($scope.isFamily) {
            angular.forEach(cordConfig.bundles[cordConfig.activeBundle].functions, function(fn){
              if(fn.id === 'url_filter'){
                $scope.levels = fn.params.levels;
              }
            });
          }

          $scope.users = res.users;
        })
        .catch(function () {
          $log.error('Problem with resource', SubscriberUsers);
        });

      $scope.updateLevel = function(user){
        // TODO save this data and show a confirmation to the user
        user.$save()
          .then(function(){
            console.log('saved');
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
    .directive('ratingsPanel', function ($log) {
      return  {
        templateUrl: 'app/view/user/ratingPanel.html',
        link: function (scope, elem, attrs) {
          function fillSubMap(order, bool) {
            var result = {};
            $.each(order, function (index, cat) {
              result[cat] = bool;
            });
            return result;
          }
          function processSubMap(prhbSites) {
            var result = {};
            $.each(prhbSites, function (index, cat) {
              result[cat] = true;
            });
            return result;
          }

          function preprocess(data, order) {
            return {
              ALL: fillSubMap(order, false),
              G: processSubMap(data.G),
              PG: processSubMap(data.PG),
              PG_13: processSubMap(data.PG_13),
              R: processSubMap(data.R),
              NONE: fillSubMap(order, true)
            };
          }

          $.getJSON('/app/data/pc_cats.json', function (data) {
            scope.level_order = data.level_order;
            scope.category_order = data.category_order;
            scope.prohibitedSites = preprocess(
              data.prohibited, data.category_order
            );
            scope.$apply();
          });
        }
      };
    });
}());
