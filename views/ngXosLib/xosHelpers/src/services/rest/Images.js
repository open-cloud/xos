(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Images
  * @description Angular resource to fetch /api/core/images/
  **/
  .service('Images', function($resource){
    return $resource('/api/core/images/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  })
})();