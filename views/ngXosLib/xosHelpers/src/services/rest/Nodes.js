(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Nodes
  * @description Angular resource to fetch /api/core/nodes/:id/
  **/
  .service('Nodes', function($resource){
    return $resource('/api/core/nodes/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  })
})();