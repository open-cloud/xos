(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name .
  * @description Angular resource to fetch Example
  **/
  .service('Example', function($resource){
    return $resource('/api/service/exampleservice/');
  })
})();