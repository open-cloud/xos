"use strict";

angular.module('cordRest', [])
  .service('User', function($http, $q, $cookies, cordConfig){
    this.login = function(username, password){
      var deferred = $q.defer();

      $http.post(cordConfig.url + '/xoslib/login/', {username: username, password: password})
      .then(function(res){
        $cookies.put('user', res.data.user);
        deferred.resolve(JSON.parse(res.data.user));
      })
      .catch(function(e){
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
      $cookies.remove('user');
      deferred.resolve();
      return deferred.promise;
    };
  })
  .service('Subscribers', function($resource, cordConfig){
    return $resource(cordConfig.url + '/xoslib/rs/subscriber');
  })
  .service('SubscriberUsers', function($resource, $filter, cordConfig, Helpers){
    // TODO define an interceptor as res.users should be resources
    // NOTE SubscriberId should ne retrieved from login information
    return $resource(cordConfig.url + '/xoslib/rs/subscriber/:subscriberId/users/:id', {}, {
      query: {
        method: 'GET',
        isArray: false,
        interceptor: {
          response: function(res){
            // this is used to fake some data that are not XOS related,
            // but can be provided by any external services

            // add an icon to the user
            res.data.users.map(function(user){
              console.log(user)
              switch (user.name){
                case 'Mom\'s PC':
                  user['icon_id'] = 'mom';
                  break
                case 'Jack\'s Laptop':
                  user['icon_id'] = 'boy2';
                  break
                case 'Jill\'s Laptop':
                  user['icon_id'] = 'girl1';
                  break
                case 'Dad\'s PC':
                  user['icon_id'] = 'dad';
                  break
              }

              return user;
            });

            // add a random login date to the user
            res.data.users.forEach(function(user){
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
    //return $resource(cordConfig.url + '/xoslib/corduser/:id')
  })
  .service('SubscriberUsersUrlFilterLevel', function($resource, cordConfig){
    return $resource(cordConfig.url + '/xoslib/rs/subscriber/:subscriberId/users/:userId/url_filter/');
  });