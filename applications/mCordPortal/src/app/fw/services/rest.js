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
  "use strict";

  function randomEnabled(){
    var levels = ["enabled", "disabled"];
    return levels[Math.round(Math.random())];
  };


  angular.module('cordRest', [])
  .factory('SetCSRFToken', function setCSRFToken($cookies) {
    return {
      request: function(request){
        request.headers['X-CSRFToken'] = $cookies.get('xoscsrftoken');
        request.headers['sessionId'] = $cookies.get('sessionid');
        return request;
      }
    };
  })
  .service('User', function($http, $q, $cookies, cordConfig){
    this.login = function(username, password){
      var deferred = $q.defer();
      var user;

      // logging in the user
      $http.post(cordConfig.url + '/api/utility/login/', {username: username, password: password})
      .then(function(res){
        $cookies.put('user', res.data.user);
        $cookies.put('sessionid', res.data.xossessionid);
        user = JSON.parse(res.data.user);
        return $http.get(cordConfig.url + '/xos/tenantrootprivileges?user=' + user.id);
      })
      .then(function(subscribers){
        // subscribers are an array because the way Django perform query
        // but one user is related to only one subscriber

        $cookies.put('subscriberId', subscribers.data[0].id);
        deferred.resolve(user);
      })
      .catch(function(e){
        deferred.reject(e);
        throw new Error(e);
      });

      return deferred.promise;
    };

    this.isLoggedIn = function(){
      var user = $cookies.get('user');
      if( angular.isDefined(user)){
        return true;
      }
      return false;
    };

    this.logout = function(){
      var deferred = $q.defer();
      var sessionId = $cookies.get('sessionid');
      $http.post(cordConfig.url + '/xoslib/logout/', {xossessionid: sessionId})
      .then(function(res){
        $cookies.remove('user');
        deferred.resolve();
      })
      .catch(function(e){
        throw new Error(e);
      });

      return deferred.promise;
    };
  })
  .service('Subscribers', function($resource, cordConfig){
    return $resource(cordConfig.url + '/xoslib/rs/subscriber');
  })
  .service('SubscriberUsers', function($resource, $filter, cordConfig, Helpers){
    return $resource(cordConfig.url + '/xoslib/rs/subscriber/:subscriberId/users/:id', {}, {
      query: {
        method: 'GET',
        isArray: true,
        cache: true,
        interceptor: {
          response: function(res){
            // this is used to fake some data that are not XOS related,
            // but can be provided by any external services

            // add an icon to the user
            res.data.map(function(user){
              switch (user.id){
                case 0:
                  user['icon_id'] = 'student1';
                  break
                case 1:
                  user['icon_id'] = 'student2';
                  break
                case 2:
                  user['icon_id'] = 'student3';
                  break
                case 3:
                  user['icon_id'] = 'student4';
                  break
              }

              user.level = randomEnabled()

              return user;
            });

            // add a random login date to the user
            res.data.forEach(function(user){
              if(!angular.isDefined(cordConfig.userActivity[user.id])){
                var date = Helpers.randomDate(new Date(2015, 0, 1), new Date());
                cordConfig.userActivity[user.id] = $filter('date')(date, 'mediumTime');
              }
            });
            return res.data;
          }
        }
      }
    });
  })
  .service('SubscriberUsersUrlFilterLevel', function($q, $http, cordConfig){
    this.updateUrlFilterLevel = function(subscriberId, userId, level){
      var deferred = $q.defer();

      $http.put(cordConfig.url + '/xoslib/rs/subscriber/' + subscriberId + '/users/' + userId + '/url_filter/' + level)
      .then(function(res){
        deferred.resolve(res);
      })
      .catch(function(e){
        throw new Error(e);
      });

      return deferred.promise;
    };
  });
}());