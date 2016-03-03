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

  angular.module('cordLogin', [])
    .controller('CordLoginCtrl', function ($log, $scope, $resource, $location, $window, User) {

      $scope.page.curr = 'login';
      $scope.loading = false;

      $scope.login = function () {
        if ($scope.email && $scope.password) {
          //getResource($scope.email);
          $scope.loading = true;
          User.login($scope.email, $scope.password)
          .then(function(user){
            $location.url('/home');
          })
          .catch(function(e){
            $scope.error = true;
          })
          .finally(function(){
            $scope.loading = false;
          });;

          $scope.shared.login = $scope.email;
        }
      };

      $log.debug('Cord Login Ctrl has been created.');
    });
}());
