(function () {
  'use strict';

  angular.module('xos.serviceTopology')
  .constant('serviceTopologyConfig', {
    widthMargin: 20,
    heightMargin: 30,
    duration: 750,
    circle: {
      radius: 10,
      r: 10,
      selectedRadius: 15
    },
    square: {
      width: 20,
      height: 20,
      x: -10,
      y: -10
    },
    rack: {
      width: 50,
      height: 50,
      x: -25,
      y: -25
    }
  })

}());