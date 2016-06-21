(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Networkstemplates
  * @description Angular resource to fetch /api/core/networktemplates/:id/
  **/
  .service('Networkstemplates', function($resource){
    return $resource('/api/core/networktemplates/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });
  })
})();
