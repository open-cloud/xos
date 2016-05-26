(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Networks
  * @description Angular resource to fetch /api/core/networks/:id/
  **/
  .service('Networks', function($resource){
    return $resource('/api/core/networks/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  })
})();
