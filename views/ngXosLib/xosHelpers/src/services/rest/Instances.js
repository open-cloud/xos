(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name .
  * @description Angular resource to fetch Instances
  **/
  .service('Instances', function($resource){
    return $resource('/api/core/instances/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  })
})();