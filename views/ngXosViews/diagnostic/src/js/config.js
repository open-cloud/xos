
/*
 * Copyright 2017-present Open Networking Foundation

 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at

 * http://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


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