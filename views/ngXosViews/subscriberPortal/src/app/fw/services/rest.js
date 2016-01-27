"use strict";

angular.module('cordRest', [])
  .service('User', function($http, $q, cordConfig){
    this.login = function(username, password){
      var deferred = $q.defer();

      $http.post(cordConfig.url + '/xoslib/login/', {username: username, password: password})
      .then(function(res){
          deferred.resolve(JSON.parse(res.data.user));
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
  .service('SubscriberUsers', function($resource, cordConfig){
    // TODO define an interceptor as res.users should be resources
    // NOTE SubscriberId should ne retrieved from login information
    return $resource(cordConfig.url + '/xoslib/rs/subscriber/:subscriberId/users/:id', {}, {
      query: {
        method: 'GET',
        isArray: false
      }
    });
    //return $resource(cordConfig.url + '/xoslib/corduser/:id')
  })
  .service('SubscriberUsersUrlFilterLevel', function($resource, cordConfig){
    return $resource(cordConfig.url + '/xoslib/rs/subscriber/:subscriberId/users/:userId/url_filter/');
  });