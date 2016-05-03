(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name .
  * @description Angular resource to fetch Truckroll
  **/
  .service('Truckroll', function($resource){
    return $resource('/api/tenant/truckroll/:truckroll_id/');
  })
})();