
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

describe('Tenant View', () => {
  
  var scope, element, isolatedScope, httpBackend;

  beforeEach(module('xos.tenant'));
  beforeEach(module('templates'));

  beforeEach(inject(function($httpBackend, $compile, $rootScope){
    
    httpBackend = $httpBackend;
    httpBackend.whenGET('/api/core/sites/?no_hyperlinks=1').respond(200, []);
    // Setting up mock request
    scope = $rootScope.$new();
    element = angular.element('<site-list></site-list>');
    $compile(element)(scope);
    scope.$digest();
    isolatedScope = element.isolateScope().vm;
  }));
  describe('site list table',() =>{
    it('site list ', () => {
      var sites = [
        {
          'name':'Mysite',
          'id':'1'
        }
      ];
      var slices = [
        {
          'site': '1',
          'instance_total' :1,
          'instance_total_ready' :1
        },
        {
          'site': '1',
          'instance_total': 2,
          'instance_total_ready': 3
        },
        {
          'site': '2',
          'instance_total': '1',
          'instance_total_ready': '2'
        }
      ];
      var result = isolatedScope.returnData(sites,slices);
      expect(result).toEqual([
        {
          'name':'Mysite',
          'id':'1',
          'instance_total':3,
          'instance_total_ready':4
        }
      ]);
    });
  });
});