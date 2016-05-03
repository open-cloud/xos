(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Instances
  * @description Angular resource to fetch /api/core/instances/:id/
  **/
  .service('Instances', function($resource){
    return $resource('/api/core/instances/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  })
})();