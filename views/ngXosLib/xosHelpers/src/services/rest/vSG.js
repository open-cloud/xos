(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.vSG
  * @description Angular resource to fetch vSG
  **/
  .service('vSG', function($resource){
    return $resource('/api/service/vsg/');
  })
})();