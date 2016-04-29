(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Users
  * @description Angular resource to fetch /api/core/users/:id/
  **/
  .service('Users', function($resource){
    return $resource('/api/core/users/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  })
})();