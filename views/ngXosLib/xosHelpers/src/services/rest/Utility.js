(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name .
  * @description Angular resource to fetch Utility
  **/
  .service('Utility', function($resource){
    return $resource('/api/utility/log');
  })
})();