
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

describe('The MCORD Slicing Topology', () => {
  
  var scope, element, isolatedScope, httpBackend;

  beforeEach(module('xos.mcord-slicing'));
  beforeEach(module('templates'));

  beforeEach(inject(function($httpBackend, $compile, $rootScope){

    httpBackend = $httpBackend;
    // Setting up mock request
    $httpBackend.expectGET('api/service/mcord_slicing_ui/topology/?no_hyperlinks=1').respond([
      {
        email: 'matteo.scandolo@gmail.com',
        firstname: 'Matteo',
        lastname: 'Scandolo'
      }
    ]);

    scope = $rootScope.$new();
    element = angular.element('<slicing-topo></slicing-topo>');
    $compile(element)(scope);
    scope.$digest();
    isolatedScope = element.isolateScope().vm;
  }));

  xit('should create 1 svg', () => {
    httpBackend.flush();
    let svg = $(element).find('svg');
    expect(svg.length).toBe(1);
  });

});