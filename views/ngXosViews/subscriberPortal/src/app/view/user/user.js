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

  var bundleUrlSuffix = '/rs/bundle',
    userUrlSuffix = '/rs/users',
    family = 'family',
    url_filter = 'url_filter';

  function randomDate(start, end) {
    return new Date(
      start.getTime() + Math.random() * (end.getTime() - start.getTime())
    );
  }

  angular.module('cordUser', [])
    .controller('CordUserCtrl', ['$log', '$scope', '$resource', '$timeout', '$filter', 'SubscriberUsers', 'cordConfig',
      function ($log, $scope, $resource, $timeout, $filter, SubscriberUsers, cordConfig) {
        var BundleData, bundleResource;
        $scope.page.curr = 'user';
        $scope.isFamily = false;
        $scope.newLevels = {};
        $scope.showCheck = false;
        $scope.ratingsShown = false;

        // === Get data functions ---

        // NOTE subscriberId should be retrieved by login
        SubscriberUsers.query({subscriberId: 1}).$promise
          .then(function(res){
            $scope.isFamily = cordConfig.bundles[0].id === 'family';
            // if bundle is family search for url_filter level
            if ($scope.isFamily) {
              angular.forEach(cordConfig.bundles[0].functions, function(fn){
                if(fn.id === 'url_filter'){
                  $scope.levels = fn.params.levels;
                }
              });
            }

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
          .catch(function () {
            $log.error('Problem with resource', bundleResource);
          });

        $scope.updateLevel = function(user){
          user.$save()
            .then(function(){
              console.log('saved');
            })
            .catch(function(e){
              throw new Error(e);
            });
        };

        //function getUsers(url) {
        //  var UserData, userResource;
        //  UserData = $resource(url);
        //  userResource = UserData.get({},
        //    // success
        //    function () {
        //      $scope.users = userResource.users;
        //      if ($.isEmptyObject($scope.shared.userActivity)) {
        //        $scope.users.forEach(function (user) {
        //          var date = randomDate(new Date(2015, 0, 1),
        //            new Date());
        //
        //          $scope.shared.userActivity[user.id] =
        //            $filter('date')(date, 'mediumTime');
        //        });
        //      }
        //    },
        //    // error
        //    function () {
        //      $log.error('Problem with resource', userResource);
        //    }
        //  );
        //}
        //
        //getUsers($scope.shared.url + userUrlSuffix);

        // === Form functions ---

        function levelUrl(id, level) {
          return $scope.shared.url +
            userUrlSuffix + '/' + id + '/apply/url_filter/level/' + level;
        }

        // NOTE This will trigger one request for each user to update url_filter level
        $scope.applyChanges = function (changeLevels) {
          var requests = [];

          if ($scope.users) {
            $.each($scope.users, function (index, user) {
              var id = user.id,
                level = user.profile.url_filter.level;
              if ($scope.newLevels[id] !== level) {
                requests.push(levelUrl(id, $scope.newLevels[id]));
              }
            });

            $.each(requests, function (index, req) {
              getUsers(req);
            });
          }
          changeLevels.$setPristine();
          $scope.showCheck = true;
          $timeout(function () {
            $scope.showCheck = false;
          }, 3000);
        };

        $scope.cancelChanges = function (changeLevels) {
          if ($scope.users) {
            $.each($scope.users, function (index, user) {
              $scope.newLevels[user.id] = user.profile.url_filter.level;
            });
          }
          changeLevels.$setPristine();
          $scope.showCheck = false;
        };

        $scope.showRatings = function () {
          $scope.ratingsShown = !$scope.ratingsShown;
        };

        $log.debug('Cord User Ctrl has been created.');
      }])

    .directive('ratingsPanel', ['$log', function ($log) {
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
    }]);

}());
