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