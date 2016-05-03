(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Deployments
  * @description Angular resource to fetch Deployments
  **/
  .service('Deployments', function($resource){
    return $resource('/api/core/deployments/:id/', { id: '@id' }, {
      update: { method: 'PUT' },
    });
  })
})();