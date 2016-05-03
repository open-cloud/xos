(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.vOLT
  * @description Angular resource to fetch vOLT
  **/
  .service('vOLT', function($resource){
    return $resource('/api/tenant/cord/volt/:volt_id/');
  })
})();