(function () {
  'use strict';

  angular.module('xos.diagnostic')
  .constant('serviceTopologyConfig', {
    widthMargin: 60,
    heightMargin: 30,
    duration: 750,
    elWidths: [20, 104, 105, 104, 20], //this is not true
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
      width: 105,
      height: 50,
      x: -30,
      y: -25
    },
    computeNode: {
      width: 50,
      height: 20,
      margin: 5,
      labelHeight: 10,
      x: -25,
      y: -10
    },
    instance: {
      width: 80,
      height: 36,
      margin: 5,
      x: -40,
      y: -18
    },
    container: {
      width: 60,
      height: 130,
      margin: 5,
      x: -30,
      y: -15
    }
  })

}());