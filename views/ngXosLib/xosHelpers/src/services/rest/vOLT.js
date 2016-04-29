(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.vOLT-Collection
  * @description Angular resource to fetch /api/tenant/cord/volt/:volt_id/
  **/
  .service('vOLT-Collection', function($resource){
    return $resource('/api/tenant/cord/volt/:volt_id/', { volt_id: '@id' }, {
      update: { method: 'PUT' }
    });
  })
})();