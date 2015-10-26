'use strict';

describe('The Content Provider SPA', () => {

  var scope, element, isolatedScope, httpBackend, mockLocation;

  // injecting main module
  beforeEach(module('xos.contentProviderApp'));

  // preload Html Templates with ng-html2js
  beforeEach(module('templates'));

  beforeEach(function() {
    module(function($provide) {
      // mocking routeParams to pass 1 as id
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

    beforeEach(inject(function($compile, $rootScope) {
      scope = $rootScope.$new();
      element = angular.element('<content-provider-detail></content-provider-detail>');
      $compile(element)(scope);
      httpBackend.expectGET('/hpcapi/contentproviders/1/').respond(CPmock.CPlist[0]);
      scope.$digest();
      httpBackend.flush();
      isolatedScope = element.isolateScope().vm;
    }));

    it('should select the active service provider', () => {
      var res = isolatedScope.activeServiceProvide(1, 'http://0.0.0.0:9000/hpcapi/serviceproviders/1/');
      expect(res).toBe(true);
    });

    it('should not select a non active service provider', () => {
      var res = isolatedScope.activeServiceProvide(1, 'http://0.0.0.0:9000/hpcapi/serviceproviders/3/');
      expect(res).toBe(false);
    });

    describe('when an id is set in the route', () => {

      beforeEach(() => {
        // spy the instance update method
        spyOn(isolatedScope.cp, '$update').and.callThrough();
      });

      it('should request the correct contentProvider', () => {
        expect(isolatedScope.cp.name).toEqual(CPmock.CPlist[0].name);
      });

      it('should update a contentProvider', () => {
        isolatedScope.cp.name = 'new name';
        isolatedScope.saveContentProvider(isolatedScope.cp);
        expect(isolatedScope.cp.$update).toHaveBeenCalled();
      });
    });
  });

  describe('the contentProviderCdn directive', () => {
    beforeEach(inject(($compile, $rootScope) => {
      scope = $rootScope.$new();
      element = angular.element('<content-provider-cdn></content-provider-cdn>');
      $compile(element)(scope);
      httpBackend.expectGET('/hpcapi/contentproviders/1/').respond(CPmock.CPlist[0]);
      httpBackend.expectGET('/hpcapi/cdnprefixs/?contentProvider=1').respond([CPmock.CDNlist[0]]);
      httpBackend.expectGET('/hpcapi/cdnprefixs/').respond(CPmock.CDNlist);
      httpBackend.whenPOST('/hpcapi/cdnprefixs/').respond(CPmock.CDNlist[0]);
      httpBackend.whenDELETE('/hpcapi/cdnprefixs/5/').respond();
      scope.$digest();
      httpBackend.flush();
      isolatedScope = element.isolateScope().vm;
    }));

    it('should load associated CDN prefix', () => {
      expect(isolatedScope.cp_prf.length).toBe(1);
      expect(isolatedScope.prf.length).toBe(2);
    });

    it('should add a CDN Prefix', () => {
      isolatedScope.addPrefix({prefix: 'test.io', defaultOriginServer: '/hpcapi/originservers/2/'});
      httpBackend.flush();
      expect(isolatedScope.cp_prf.length).toBe(2);
    });

    it('should remove a CDN Prefix', () => {
      isolatedScope.removePrefix(isolatedScope.cp_prf[0]);
      httpBackend.flush();
      expect(isolatedScope.cp_prf.length).toBe(0);
    });
  });

  describe('the contentProviderServer directive', () => {
    beforeEach(inject(($compile, $rootScope) => {
      scope = $rootScope.$new();
      element = angular.element('<content-provider-server></content-provider-server>');
      $compile(element)(scope);
      httpBackend.expectGET('/hpcapi/contentproviders/1/').respond(CPmock.CPlist[0]);
      httpBackend.expectGET('/hpcapi/originservers/?contentProvider=1').respond(CPmock.OSlist);
      httpBackend.whenPOST('/hpcapi/originservers/').respond(CPmock.OSlist[0]);
      httpBackend.whenDELETE('/hpcapi/originservers/8/').respond();
      scope.$digest();
      httpBackend.flush();
      isolatedScope = element.isolateScope().vm;
    }));

    it('should load associated OriginServer', () => {
      expect(isolatedScope.cp_os.length).toBe(4);
    });

    it('should add a OriginServer', () => {
      isolatedScope.addOrigin({protocol: 'http', url: 'test.io'});
      httpBackend.flush();
      expect(isolatedScope.cp_os.length).toBe(5);
    });

    it('should remove a OriginServer', () => {
      isolatedScope.removeOrigin(isolatedScope.cp_os[0]);
      httpBackend.flush();
      expect(isolatedScope.cp_os.length).toBe(3);
    });
  });
});
