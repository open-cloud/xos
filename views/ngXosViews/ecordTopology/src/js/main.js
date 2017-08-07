
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


'use strict';

angular.module('xos.ecordTopology', [
  'ngResource',
  'ngCookies',
  'ui.router',
  'xos.helpers',
  'ui.checkbox'
])
.config(($stateProvider) => {
  $stateProvider
  .state('ecord-topo', {
    url: '/',
    template: '<ecord-topo></ecord-topo>'
  })
  .state('eline-create', {
    url: '/eline',
    template: '<eline-form></eline-form>'
  })
  .state('eline-details', {
    url: '/eline/:id',
    template: '<eline-details></eline-details>'
  });
})
.config(function($httpProvider){
  $httpProvider.interceptors.push('NoHyperlinks');
})
.constant('cordIcons', {
  cordLogo: `M92.5,62.3l-33,33,2.5,2.5c4.1,4.1,7.4,3.6,11.2-.1L95.9,75l-4.5-4.5,4.7-4.7-3.6-3.6Zm2.6,7L98.4,66l3.3,3.3-3.3,3.3-3.3-3.3ZM94.5,60l4.9-4.9,4.9,4.9-4.9,4.9ZM36.2,36.1L18.6,53.8c-7.8,7.8-5.8,17.4-2.4,22l-2.2-2.2c-10.6-10.6-11.2-20,0-31.2L28.2,28.1L31.3,25l8,8-3.1,3.1ZM55.5,55.4l3.6-3.6L66.9,44l-8-8l-2.5,2.5-5.2,5.2l-3.6,3.6L33.2,61.6C22,72.7,22.5,82.2,33.2,92.8L35.4,95c-3.4-4.5-5.4-14.1,2.4-22L55.5,55.4ZM50.7,21.7l-8-8L35,21.2l8,8,7.6-7.6ZM62.8,9.6L55.4,17l-8-8,7.4-7.4,8,8Zm0.7,18.3-7.6,7.6-8-8,7.6-7.6,8,8Zm26.1-6.6-8.1,8.1-8-8,8.1-8.1,8,8ZM79.3,31.5l-7.4,7.4-8-8,7.4-7.4,8,8ZM45.7,45.6L54.3,37l-8-8-8.6,8.6L23.4,51.8C12.2,63,12.8,72.4,23.4,83l2.2,2.2c-3.4-4.5-5.4-14.1,2.4-22ZM34.9,80.7l20.6,20.5c2,2,4.6,4.1,7.9,3.2-2.9,2.9-8.9,1.7-11.9-1.3L35.1,86.8,35,86.6H34.9l-0.8-.8a15,15,0,0,1,.1-1.9,14.7,14.7,0,0,1,.7-3.2Zm-0.6,7.4a21.3,21.3,0,0,0,5.9,11.7l5.7,5.7c3,3,9,4.1,11.9,1.3-3.3.9-5.9-1.2-7.9-3.2L34.3,88.1Zm3.5-12.4a16.6,16.6,0,0,0-2.3,3.6L57,100.8c3,3,9,4.1,11.9,1.3-3.3.9-5.9-1.2-7.9-3.2Z`,
  service: `M2.16,10.77l2.7-.44a0.36,0.36,0,0,0,.21-0.2c0.24-.55.47-1.1,0.69-1.65a0.42,0.42,0,0,0,0-.33c-0.5-.74-1-1.47-1.52-2.18L5.94,4.22,8.07,5.75a0.37,0.37,0,0,0,.44,0C9,5.55,9.52,5.36,10,5.16a0.36,0.36,0,0,0,.27-0.32c0.13-.87.28-1.74,0.42-2.64l0.23,0c0.66,0,1.32,0,2,0a0.25,0.25,0,0,1,.3.26c0.13,0.81.28,1.62,0.41,2.44a0.34,0.34,0,0,0,.26.3c0.52,0.2,1,.41,1.54.64a0.34,0.34,0,0,0,.4,0l1.93-1.4L18,4.22,19.76,6c-0.49.7-1,1.43-1.52,2.16a0.4,0.4,0,0,0,0,.47c0.23,0.49.43,1,.62,1.49a0.36,0.36,0,0,0,.32.27l2.66,0.43v2.45l-1.63.29c-0.36.06-.72,0.11-1.07,0.19a0.43,0.43,0,0,0-.26.22c-0.23.53-.43,1.07-0.67,1.6a0.31,0.31,0,0,0,0,.37l1.4,1.94,0.17,0.24-1.74,1.74c-0.69-.48-1.41-1-2.13-1.5a0.43,0.43,0,0,0-.52,0,13.34,13.34,0,0,1-1.43.6,0.4,0.4,0,0,0-.32.35c-0.14.86-.3,1.72-0.46,2.59H10.73c-0.14-.85-0.29-1.7-0.42-2.55A0.43,0.43,0,0,0,10,18.88c-0.5-.18-1-0.39-1.46-0.61a0.36,0.36,0,0,0-.42,0c-0.73.52-1.46,1-2.17,1.52L4.16,18.08l0.37-.52c0.39-.55.78-1.1,1.19-1.65a0.31,0.31,0,0,0,0-.37C5.52,15,5.3,14.5,5.09,14A0.34,0.34,0,0,0,4.8,13.7l-2.64-.46V10.77ZM15.43,12A3.45,3.45,0,1,0,12,15.48,3.46,3.46,0,0,0,15.43,12Z`
})
.directive('ecordTopo', function(){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/ecord-topo.tpl.html',
    controller: function(Eline, $location){

      // retrieving user list
      Eline.query().$promise
      .then((elines) => {
        this.elines = elines;
      })
      .catch((e) => {
        throw new Error(e);
      });

      this.selectEline = (eline) => {
        $location.path(`/eline/${eline.id}`)
      }
    }
  };
});