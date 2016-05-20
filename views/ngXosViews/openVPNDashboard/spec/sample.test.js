'use strict';

describe('The User List', () => {
  
  var scope, element, isolatedScope, httpBackend;

  beforeEach(module('xos.openVPNDashboard'));
  beforeEach(module('templates'));

  beforeEach(inject(function($httpBackend, $compile, $rootScope){
    
    httpBackend = $httpBackend;
    // Setting up mock request
    $httpBackend.expectGET('/api/tenant/openvpn/list/?no_hyperlinks=1').respond([
      {
        email: 'jermowery@email.arizona.edu',
        firstname: 'Jeremy',
        lastname: 'Mowery' 
      }
    ]);
  
    scope = $rootScope.$new();
    element = angular.element('<vpn-list></vpn-list>');
    $compile(element)(scope);
    scope.$digest();
    isolatedScope = element.isolateScope().vm;
  }));

  it('should load 1 vpn', () => {
    httpBackend.flush();
    expect(isolatedScope.vpns.length).toBe(1);
  });

});