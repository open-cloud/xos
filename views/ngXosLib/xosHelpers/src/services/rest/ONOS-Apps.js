(function() {
  'use strict';

  angular.module('xos.helpers')
  .service('ONOS-App-Collection', function($resource){
    return $resource('/api/tenant/onos/app/');
  })
})();