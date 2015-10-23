'use strict';

describe('The Content Provider SPA', () => {

  var scope, element, isolatedScope, httpBackend, mockLocation;

  // injecting main module
  beforeEach(module('xos.contentProviderApp'));

  // preload Html Templates with ng-html2js
  beforeEach(module('templates'));

  beforeEach(inject(function(_$location_, $httpBackend) {
    spyOn(_$location_, 'url');
    mockLocation = _$location_;
    httpBackend = $httpBackend;
    // Setting up mock request
    $httpBackend.whenGET('/hpcapi/contentproviders/').respond(CPmock.list);
    $httpBackend.whenDELETE('/hpcapi/contentproviders/1/').respond();
  }));

  describe('the action directive', () => {
    beforeEach(inject(function($compile, $rootScope) {
      scope = $rootScope.$new();

      element = angular.element('<cp-actions id="\'1\'"></cp-actions>');
      $compile(element)(scope);
      scope.$digest();
      isolatedScope = element.isolateScope().vm;
    }));

    it('should delete an element and redirect to list', () => {
      isolatedScope.deleteCp(1);
      httpBackend.flush();
      expect(mockLocation.url).toHaveBeenCalled();
    });
  });

  describe('the contentProvider list', () => {
    beforeEach(inject(function($compile, $rootScope) {
      scope = $rootScope.$new();

      element = angular.element('<content-provider-list></content-provider-list>');
      $compile(element)(scope);
      scope.$digest();
      httpBackend.flush();
      isolatedScope = element.isolateScope().vm;
    }));


    it('should load 2 contentProvider', () => {
      expect(isolatedScope.contentProviderList.length).toBe(2);
    });

    it('should delete a contentProvider', () => {
      isolatedScope.deleteCp(1);
      httpBackend.flush();
      expect(isolatedScope.contentProviderList.length).toBe(1);
    });
  });
});
