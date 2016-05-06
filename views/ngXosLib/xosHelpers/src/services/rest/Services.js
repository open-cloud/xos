(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Services
  * @description Angular resource to fetch /api/core/services/:id/
  **/
  .service('Services', function($resource){
    return $resource('/api/core/services/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  })
})();