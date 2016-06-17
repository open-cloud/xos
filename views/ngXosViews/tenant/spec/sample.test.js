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
    element = angular.element('<users-list></users-list>');
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