(function () {
  'use strict';

  angular.module('xos.serviceTopology')
    .factory('d3', function($window){
      return $window.d3;
    })
  .service('TreeLayout', function(){
    this.updateTree = (source) => {

    }
  });

}());