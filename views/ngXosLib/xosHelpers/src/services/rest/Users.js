(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name .
  * @description Angular resource to fetch Users
  **/
  .service('Users', function($resource){
    return $resource('/api/core/users/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  })
})();