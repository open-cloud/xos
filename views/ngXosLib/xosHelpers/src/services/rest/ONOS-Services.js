(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name .
  * @description Angular resource to fetch ONOS Services
  **/
  .service('ONOS Services', function($resource){
    return $resource('/api/service/onos/');
  })
})();