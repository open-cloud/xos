'use strict';

describe('The Content Provider SPA', () => {

  var scope, element, isolatedScope, httpBackend, mockLocation;

  // injecting main module
  beforeEach(module('xos.contentProviderApp'));

  // preload Html Templates with ng-html2js
  beforeEach(module('templates'));

  beforeEach(function() {
    module(function($provide) {
      $provide.provider('$routeParams', function() {
        this.$get = function() {
          return {id: 1};
        };
      });
    });
  });

  beforeEach(inject(function(_$location_, $httpBackend) {
    spyOn(_$location_, 'url');
    mockLocation = _$location_;
    httpBackend = $httpBackend;
    // Setting up mock request
    $httpBackend.whenGET('/hpcapi/contentproviders/').respond(CPmock.CPlist);
    $httpBackend.whenGET('/hpcapi/serviceproviders/').respond(CPmock.SPlist);
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

  describe('the contentProviderDetail directive', () => {
    describe('when an id is set in the route', () => {

      beforeEach(inject(function($compile, $rootScope, ContentProvider) {
        scope = $rootScope.$new();

        httpBackend.expectGET('/hpcapi/contentproviders/1/').respond(CPmock.CPlist[0]);
        httpBackend.whenPUT('/hpcapi/contentproviders/1/').respond({name: 'done'});

        spyOn(ContentProvider, 'save').and.callThrough();

        element = angular.element('<content-provider-detail></content-provider-detail>');
        $compile(element)(scope);
        scope.$digest();
        httpBackend.flush();
        isolatedScope = element.isolateScope().vm;
      }));

      it('should request the correct contentProvider', () => {
        expect(isolatedScope.cp.name).toEqual(CPmock.CPlist[0].name);
      });

      it('should update a contentProvider', () => {
        isolatedScope.cp.name = 'new name';
        isolatedScope.saveContentProvider(isolatedScope.cp);
        httpBackend.flush();
        expect(isolatedScope.cp.name).toEqual('done');
      });
    });
  });
});
