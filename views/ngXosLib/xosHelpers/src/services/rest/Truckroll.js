(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Truckroll
  * @description Angular resource to fetch Truckroll
  **/
  .service('Truckroll', function($resource){
    return $resource('/api/tenant/truckroll/:truckroll_id/');
  })
})();