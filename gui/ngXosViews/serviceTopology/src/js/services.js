(function () {
  'use strict';

  angular.module('xos.serviceTopology')
  .service('Services', function($resource){
    return $resource('/xos/services');
  });

}());