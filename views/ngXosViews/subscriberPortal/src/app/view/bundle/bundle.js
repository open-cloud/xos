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

  var urlSuffix = '/rs/bundle';

  var basic = 'basic',
    family = 'family';

  angular.module('cordBundle', [])
    .controller('CordBundleCtrl', function ($log, $scope, $resource, cordConfig) {
      var BundleData, resource,
        getData;
      $scope.page.curr = 'bundle';
      $scope.show = false;

      // set the current bundle
      $scope.name = cordConfig.bundles[cordConfig.activeBundle].name;
      $scope.desc = cordConfig.bundles[cordConfig.activeBundle].desc;
      $scope.funcs = cordConfig.bundles[cordConfig.activeBundle].functions;

      // set the available bundle
      if(cordConfig.activeBundle === 0) {
        $scope.available = cordConfig.bundles[1];
      }
      else{
        $scope.available = cordConfig.bundles[0];
      }

      // switching the bundles
      $scope.changeBundle = function (id) {
        if(cordConfig.activeBundle === 0){
          cordConfig.activeBundle = 1;
          $scope.available = cordConfig.bundles[0];
        }
        else{
          cordConfig.activeBundle = 0;
          $scope.available = cordConfig.bundles[1];
        }
        $scope.name = cordConfig.bundles[cordConfig.activeBundle].name;
        $scope.desc = cordConfig.bundles[cordConfig.activeBundle].desc;
        $scope.funcs = cordConfig.bundles[cordConfig.activeBundle].functions;
      };

      // hiding and showing bundles
      $scope.showBundles = function () {
        $scope.show = !$scope.show;
      };

      $log.debug('Cord Bundle Ctrl has been created.');
    })
    .directive('bundleAvailable', function () {
      return {
        templateUrl: 'app/view/bundle/available.html'
      };
    });
}());
