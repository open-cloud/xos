(function () {
  'use strict';

  angular.module('xos.diagnostic')
  .factory('d3', function($window){
    return $window.d3;
  })

}());