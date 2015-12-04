'use strict';

describe('The User List', () => {
  
  var scope, element, isolatedScope, httpBackend;

  beforeEach(module('xos.ceilometerDashboard'));
  beforeEach(module('templates'));

  beforeEach(inject(function($httpBackend, $compile, $rootScope){

    httpBackend = $httpBackend;
    // Setting up mock request
    $httpBackend.expectGET(/meters/).respond([
      {
        email: 'teo@onlab.us',
        firstname: 'Matteo',
        lastname: 'Scandolo'
      }
    ]);
  
    scope = $rootScope.$new();
    element = angular.element('<ceilometer-dashboard></ceilometer-dashboard>');
    $compile(element)(scope);
    scope.$digest();
    isolatedScope = element.isolateScope().vm;
  }));

  it('should load 1 users', () => {
    httpBackend.flush();
    expect(isolatedScope.meters.length).toBe(1);
  });

});