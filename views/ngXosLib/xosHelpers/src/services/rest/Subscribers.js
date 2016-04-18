(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Subscribers
  * @description Angular resource to fetch /api/tenant/cord/subscriber/:subscriber_id/
  **/
  .service('Subscribers', function($resource){
    return $resource('/api/tenant/cord/subscriber/:subscriber_id/', { subscriber_id: '@id' });
  })
  /**
  * @ngdoc service
  * @name xos.helpers.Subscriber-features
  * @description Angular resource to fetch /api/tenant/cord/subscriber/:subscriber_id/features/
  **/
  .service('Subscriber-features', function($resource){
    return $resource('/api/tenant/cord/subscriber/:subscriber_id/features/', { subscriber_id: '@id' });
  })
  /**
  * @ngdoc service
  * @name xos.helpers.Subscriber-features-uplink_speed
  * @description Angular resource to fetch /api/tenant/cord/subscriber/:subscriber_id/features/uplink_speed/
  **/
  .service('Subscriber-features-uplink_speed', function($resource){
    return $resource('/api/tenant/cord/subscriber/:subscriber_id/features/uplink_speed/', { subscriber_id: '@id' });
  })
  /**
  * @ngdoc service
  * @name xos.helpers.Subscriber-features-downlink_speed
  * @description Angular resource to fetch /api/tenant/cord/subscriber/:subscriber_id/features/downlink_speed/
  **/
  .service('Subscriber-features-downlink_speed', function($resource){
    return $resource('/api/tenant/cord/subscriber/:subscriber_id/features/downlink_speed/', { subscriber_id: '@id' });
  })
  /**
  * @ngdoc service
  * @name xos.helpers.Subscriber-features-cdn
  * @description Angular resource to fetch /api/tenant/cord/subscriber/:subscriber_id/features/cdn/
  **/
  .service('Subscriber-features-cdn', function($resource){
    return $resource('/api/tenant/cord/subscriber/:subscriber_id/features/cdn/', { subscriber_id: '@id' });
  })
  /**
  * @ngdoc service
  * @name xos.helpers.Subscriber-features-uverse
  * @description Angular resource to fetch /api/tenant/cord/subscriber/:subscriber_id/features/uverse/
  **/
  .service('Subscriber-features-uverse', function($resource){
    return $resource('/api/tenant/cord/subscriber/:subscriber_id/features/uverse/', { subscriber_id: '@id' });
  })
  /**
  * @ngdoc service
  * @name xos.helpers.Subscriber-features-status
  * @description Angular resource to fetch /api/tenant/cord/subscriber/:subscriber_id/features/status/
  **/
  .service('Subscriber-features-status', function($resource){
    return $resource('/api/tenant/cord/subscriber/:subscriber_id/features/status/', { subscriber_id: '@id' });
  })
})();