'use strict';

/*
 * Resource related to the CORD Subscribers.

 */

angular.module('xos.helpers')
.service('Subscribers', function($resource){
  return $resource('/api/tenant/cord/subscriber/:subscriber_id/', { subscriber_id: '@id'});
})
.service('Subscriber-features', function($resource){
  return $resource('/api/tenant/cord/subscriber/:subscriber_id/features/', { subscriber_id: '@id'});
})
.service('Subscriber-features-uplink_speed', function($resource){
  return $resource('/api/tenant/cord/subscriber/:subscriber_id/features/uplink_speed/', { subscriber_id: '@id'});
})
.service('Subscriber-features-downlink_speed', function($resource){
  return $resource('/api/tenant/cord/subscriber/:subscriber_id/features/downlink_speed/', { subscriber_id: '@id'});
})
.service('Subscriber-features-cdn', function($resource){
  return $resource('/api/tenant/cord/subscriber/:subscriber_id/features/cdn/', { subscriber_id: '@id'});
})
.service('Subscriber-features-uverse', function($resource){
  return $resource('/api/tenant/cord/subscriber/:subscriber_id/features/uverse/', { subscriber_id: '@id'});
})
.service('Subscriber-features-status', function($resource){
  return $resource('/api/tenant/cord/subscriber/:subscriber_id/features/status/', { subscriber_id: '@id'});
})
