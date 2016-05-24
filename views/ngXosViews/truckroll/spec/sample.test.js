'use strict';

describe('The User List', () => {
  
  var scope, element, isolatedScope, httpBackend;

  beforeEach(module('xos.truckroll'));
  beforeEach(module('templates'));

  beforeEach(inject(function($httpBackend, $compile, $rootScope){
    
    httpBackend = $httpBackend;
    // Setting up mock request
    $httpBackend.expectGET('/api/tenant/cord/subscriber/?no_hyperlinks=1').respond([
      {
        email: 'teo@onlab.us',
        firstname: 'Matteo',
        lastname: 'Scandolo' 
      }
    ]);
  
    scope = $rootScope.$new();
    element = angular.element('<truckroll></truckroll>');
    $compile(element)(scope);
    scope.$digest();
    isolatedScope = element.isolateScope().vm;
  }));

  it('should load 1 subscriber', () => {
    httpBackend.flush();
    expect(isolatedScope.subscribers.length).toBe(1);
  });

});