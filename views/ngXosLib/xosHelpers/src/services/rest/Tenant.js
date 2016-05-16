(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Tenant
  * @description Angular resource to fetch /api/core/tenant/:id/
  **/
  .service('Tenants', function($resource){
    return $resource('/api/core/tenants/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  })
})();