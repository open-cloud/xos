(function() {
  'use strict';

  angular.module('xos.helpers')
  .service('vSG-Collection', function($resource){
    return $resource('/api/service/vsg/');
  })
})();