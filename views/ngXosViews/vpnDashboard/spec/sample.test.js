'use strict';

describe('The User List', () => {
  
  var scope, element, isolatedScope, httpBackend;

  beforeEach(module('xos.vpnDashboard'));
  beforeEach(module('templates'));

  beforeEach(inject(function($httpBackend, $compile, $rootScope){
    
    httpBackend = $httpBackend;
    // Setting up mock request
    $httpBackend.expectGET('/xos/users/?no_hyperlinks=1').respond([
      {
        email: 'jermowery@email.arizona.edu',
        firstname: 'Jeremy',
        lastname: 'Mowery' 
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
    expect(isolatedScope.users[0].email).toEqual('jermowery@email.arizona.edu');
    expect(isolatedScope.users[0].firstname).toEqual('Jeremy');
    expect(isolatedScope.users[0].lastname).toEqual('Mowery');
  });

});