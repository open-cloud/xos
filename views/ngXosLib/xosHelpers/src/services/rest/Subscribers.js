(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name .
  * @description Angular resource to fetch Subscribers
  **/
  .service('Subscribers', function($resource){
    return $resource('/api/tenant/cord/subscriber/:subscriber_id/');
  })
})();