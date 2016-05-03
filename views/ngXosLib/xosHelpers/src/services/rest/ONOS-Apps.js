(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.ONOS Apps
  * @description Angular resource to fetch ONOS Apps
  **/
  .service('ONOS Apps', function($resource){
    return $resource('/api/tenant/onos/app/');
  })
})();