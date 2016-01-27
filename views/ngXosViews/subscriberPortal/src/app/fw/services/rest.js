"use strict";

angular.module('cordRest', [])
  .service('Subscribers', function($resource, cordConfig){
    return $resource(cordConfig.url + '/xoslib/rs/subscriber');
  })
  .service('SubscriberUsers', function($resource, cordConfig){
    // NOTE SubscriberId should ne retrieved from login information
    return $resource(cordConfig.url + '/xoslib/rs/subscriber/:subscriberId/users/:id', {}, {
      query: {
        method: 'GET',
        isArray: false
      }
    });
  });