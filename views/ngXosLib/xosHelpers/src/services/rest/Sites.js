(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Sites
  * @description Angular resource to fetch /api/core/sites/:id/
  **/
  .service('Sites', function($resource){
    return $resource('/api/core/sites/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  })
})();