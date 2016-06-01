'use strict';

describe('The User List', () => {
  
  var scope, element, isolatedScope, httpBackend;

  beforeEach(module('xos.synchronizerNotifier'));
  beforeEach(module('templates'));

  beforeEach(inject(function($httpBackend, $compile, $rootScope){
    
    httpBackend = $httpBackend;
    // Setting up mock request
    $httpBackend.expectGET('/api/core/users/?no_hyperlinks=1').respond([
      {
        email: 'matteo.scandolo@gmail.com',
        firstname: 'Matteo',
        lastname: 'Scandolo' 
      }
    ]);
  
    scope = $rootScope.$new();
    element = angular.element('<users-list></users-list>');
    $compile(element)(scope);
    scope.$digest();
    isolatedScope = element.isolateScope().vm;
  }));

  xit('should load 1 users', () => {
    httpBackend.flush();
    expect(isolatedScope.users.length).toBe(1);
    expect(isolatedScope.users[0].email).toEqual('matteo.scandolo@gmail.com');
    expect(isolatedScope.users[0].firstname).toEqual('Matteo');
    expect(isolatedScope.users[0].lastname).toEqual('Scandolo');
  });

});