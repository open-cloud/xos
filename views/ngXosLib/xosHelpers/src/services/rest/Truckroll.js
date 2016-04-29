(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Truckroll-Collection
  * @description Angular resource to fetch /api/tenant/truckroll/:truckroll_id/
  **/
  .service('Truckroll-Collection', function($resource){
    return $resource('/api/tenant/truckroll/:truckroll_id/', { truckroll_id: '@id' }, {
      update: { method: 'PUT' }
    });
  })
})();