'use strict';

describe('The User List', () => {
  
  var scope, element, isolatedScope, httpBackend;

  beforeEach(module('xos.<%= name %>'));
  beforeEach(module('templates'));

  beforeEach(inject(function($httpBackend, $compile, $rootScope){
    
    httpBackend = $httpBackend;
    // Setting up mock request
    $httpBackend.expectGET('/api/core/users/?no_hyperlinks=1').respond([
      {
        email: '<%= user.email %>',
        firstname: '<%= user.firstname %>',
        lastname: '<%= user.lastname %>' 
      }
    ]);
  
    scope = $rootScope.$new();
    element = angular.element('<users-list></users-list>');
    $compile(element)(scope);
    scope.$digest();
    isolatedScope = element.isolateScope().vm;
  }));

  it('should load 1 users', () => {
    httpBackend.flush();
    expect(isolatedScope.users.length).toBe(1);
    expect(isolatedScope.users[0].email).toEqual('<%= user.email %>');
    expect(isolatedScope.users[0].firstname).toEqual('<%= user.firstname %>');
    expect(isolatedScope.users[0].lastname).toEqual('<%= user.lastname %>');
  });

});