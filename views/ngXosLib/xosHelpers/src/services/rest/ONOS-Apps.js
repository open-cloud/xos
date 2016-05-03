(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name .
  * @description Angular resource to fetch ONOS Apps
  **/
  .service('ONOS Apps', function($resource){
    return $resource('/api/tenant/onos/app/');
  })
})();