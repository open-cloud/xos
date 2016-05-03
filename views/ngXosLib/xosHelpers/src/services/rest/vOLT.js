(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name .
  * @description Angular resource to fetch vOLT
  **/
  .service('vOLT', function($resource){
    return $resource('/api/tenant/cord/volt/:volt_id/');
  })
})();