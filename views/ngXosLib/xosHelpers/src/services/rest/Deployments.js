(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name .
  * @description Angular resource to fetch Deployments
  **/
  .service('Deployments', function($resource){
    return $resource('/api/core/deployments/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  })
})();