(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Instances
  * @description Angular resource to fetch /api/core/instances/:instance_id/
  **/
  .service('Instances', function($resource){
    return $resource('/api/core/instances/:instance_id/', { instance_id: '@id' });
  })
})();