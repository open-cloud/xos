(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Truckroll
  * @description Angular resource to fetch /api/tenant/truckroll/:id/
  **/
  .service('Truckroll', function($resource){
    return $resource('/api/tenant/truckroll/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  })
})();
