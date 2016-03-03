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

  var modules = [
      'ngRoute',
      'ngResource',
      'ngAnimate',
      'ngCookies',
      'cordRest',
      'cordMast',
      'cordFoot',
      'cordLogin',
      'cordHome',
      'cordUser',
      'cordBundle'
    ];

  angular.module('cordGui', modules)
    .config(function ($routeProvider, $httpProvider) {

      $httpProvider.interceptors.push('SetCSRFToken');

      $routeProvider
        .when('/login', {
          controller: 'CordLoginCtrl',
          controllerAs: 'ctrl',
          templateUrl: 'app/view/login/login.html'
        })
        .when('/home', {
          controller: 'CordHomeCtrl',
          controllerAs: 'ctrl',
          templateUrl: 'app/view/home/home.html'
        })
        .when('/user', {
          controller: 'CordUserCtrl',
          controllerAs: 'ctrl',
          templateUrl: 'app/view/user/user.html'
        })
        .when('/bundle', {
          controller: 'CordBundleCtrl',
          controllerAs: 'ctrl',
          templateUrl: 'app/view/bundle/bundle.html'
        })
        .otherwise({
          redirectTo: '/login'
        });
    })
    .controller('CordCtrl', function ($scope, $location, cordConfig) {
      $scope.shared = {
        url: 'http://' + $location.host() + ':' + $location.port()
      };
      $scope.shared.userActivity = cordConfig.userActivity;
      $scope.page = {};
    })
    .constant('cordConfig', {
      url: '',
      userActivity: {}, //check if really needed
      activeBundle: 1,
      bundles: [
        {
          "id": "family",
          "name": "Education Bundle",
          "desc": "Description for advanced bundle and the amazing thing it can do to managing Video Optimization.",
          "functions": [
            {
              "id": "cache",
              "name": "Cache",
              "desc": "Local content and frequently used content are served from local cache service entity. This will increase the quality of service by reduced delay and by avoiding the bottleneck of the legacy cloud based content services.",
              "params": {}
            },
            {
              "id": "firewall",
              "name": "Firewall",
              "desc": "This provides security services that control the incoming and outgoing network traffic. Enhanced features like IPS (Intrusion Prevention System), threat analysis and content filtering are also available.",
              "params": {}
            },
            {
              "id": "video",
              "name": "Video Optimization",
              "desc": "This can provide different video transcoding formats to improve video quality during congestion.Priority based badwidth resource allocation is also available",
              "params": {
                "levels": ["enabled", "disabled"]
              }
            }
          ]
        },
        {
          "id": "basic",
          "name": "Basic Bundle",
          "desc": "Description for basic bundle",
          "functions": [
            {
              "id": "cache",
              "name": "Cache",
              "desc": "Local content and frequently used content are served from local cache service entity. This will increase the quality of service by reduced delay and by avoiding the bottleneck of the legacy cloud based content services.",
              "params": {}
            },
            {
              "id": "firewall",
              "name": "Firewall",
              "desc": "This provides security services that control the incoming and outgoing network traffic. Enhanced features like IPS (Intrusion Prevention System), threat analysis and content filtering are also available.",
              "params": {}
            }
          ]
        }
      ]
    })
    .run(function($rootScope, $location, cordConfig, User){
      cordConfig.url = 'http://' + $location.host() + ':' + $location.port();

      // basic authentication
      $rootScope.$on('$routeChangeStart', function(next, current) {
        if(!User.isLoggedIn()){
          $location.path('/login');
        }
      });
    });
}());
