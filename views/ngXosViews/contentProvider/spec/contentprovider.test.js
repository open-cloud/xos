'use strict';

describe('The Content Provider SPA', () => {

  var scope, element, isolatedScope, httpBackend, mockLocation, httpProvider;

  var token = 'fakeToken';

  // injecting main module
  beforeEach(module('xos.contentProvider'));

  beforeEach(module('templates'));

  beforeEach(function(){
    module(function($provide, $httpProvider){

      httpProvider = $httpProvider;

      // mocking stateParams to pass 1 as id
      $provide.provider('$stateParams', function(){
        /* eslint-disable no-invalid-this*/
        this.$get = function(){
          return {id: 1};
        };
        /* eslint-enable no-invalid-this*/
      });

      //mock $cookie to return a fake xoscsrftoken
      $provide.service('$cookies', function(){
        /* eslint-disable no-invalid-this*/
        this.get = () => {
          return token;
        };
        /* eslint-enable no-invalid-this*/
      });
    });
  });

  beforeEach(inject(function(_$location_, $httpBackend){
    spyOn(_$location_, 'url');
    mockLocation = _$location_;
    httpBackend = $httpBackend;
    // Setting up mock request
    $httpBackend.whenGET('/hpcapi/contentproviders/?no_hyperlinks=1').respond(CPmock.CPlist);
    $httpBackend.whenGET('/hpcapi/serviceproviders/?no_hyperlinks=1').respond(CPmock.SPlist);
    $httpBackend.whenDELETE('/hpcapi/contentproviders/1/?no_hyperlinks=1').respond();
  }));

  xit('should set the $http interceptor', () => {
    expect(httpProvider.interceptors).toContain('SetCSRFToken');
  });

  xit('should add no_hyperlink param', inject(($http, $httpBackend) => {
    $http.get('www.example.com');
    $httpBackend.expectGET('www.example.com?no_hyperlinks=1').respond(200);
    $httpBackend.flush();
  }));

  xit('should set token in the headers', inject(($http, $httpBackend) => {
    $http.post('http://example.com');
    $httpBackend.expectPOST('http://example.com?no_hyperlinks=1', undefined, function(headers){
      // if this condition is false the httpBackend expectation fail
      return headers['X-CSRFToken'] === token;
    }).respond(200, {name: 'example'});
    httpBackend.flush();
  }));

  describe('the action directive', () => {
    beforeEach(inject(function($compile, $rootScope){
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
    beforeEach(inject(function($compile, $rootScope){
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

    beforeEach(inject(function($compile, $rootScope){
      scope = $rootScope.$new();
      element = angular.element('<content-provider-detail></content-provider-detail>');
      $compile(element)(scope);
      httpBackend.expectGET('/hpcapi/contentproviders/1/?no_hyperlinks=1').respond(CPmock.CPlist[0]);
      scope.$digest();
      httpBackend.flush();
      isolatedScope = element.isolateScope().vm;
    }));

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
      httpBackend.expectGET('/hpcapi/contentproviders/1/?no_hyperlinks=1').respond(CPmock.CPlist[0]);
      // httpBackend.expectGET('/hpcapi/cdnprefixs/?no_hyperlinks=1&contentProvider=1').respond([CPmock.CDNlist[0]]);
      httpBackend.expectGET('/hpcapi/cdnprefixs/?no_hyperlinks=1').respond(CPmock.CDNlist);
      httpBackend.whenPOST('/hpcapi/cdnprefixs/?no_hyperlinks=1').respond(CPmock.CDNlist[0]);
      httpBackend.whenDELETE('/hpcapi/cdnprefixs/5/?no_hyperlinks=1').respond();
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
      httpBackend.expectGET('/hpcapi/contentproviders/1/?no_hyperlinks=1').respond(CPmock.CPlist[0]);
      httpBackend.expectGET('/hpcapi/originservers/?no_hyperlinks=1&contentProvider=1').respond(CPmock.OSlist);
      httpBackend.whenPOST('/hpcapi/originservers/?no_hyperlinks=1').respond(CPmock.OSlist[0]);
      httpBackend.whenDELETE('/hpcapi/originservers/8/?no_hyperlinks=1').respond();
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

  describe('the contentProviderUsers directive', () => {
    beforeEach(inject(($compile, $rootScope) => {
      scope = $rootScope.$new();
      element = angular.element('<content-provider-users></content-provider-users>');
      $compile(element)(scope);
      httpBackend.expectGET('/xos/users/?no_hyperlinks=1').respond(CPmock.UserList);
      httpBackend.expectGET('/hpcapi/contentproviders/1/?no_hyperlinks=1').respond(CPmock.CPlist[0]);
      httpBackend.whenPUT('/hpcapi/contentproviders/1/?no_hyperlinks=1').respond(CPmock.CPlist[0]);
      scope.$digest();
      httpBackend.flush();
      isolatedScope = element.isolateScope().vm;
    }));

    it('should render one user', () => {
      expect(isolatedScope.cp.users.length).toBe(1);
      expect(typeof isolatedScope.cp.users[0]).toEqual('object');
    });

    it('should add a user', () => {
      isolatedScope.addUserToCp({name: 'teo'});
      expect(isolatedScope.cp.users.length).toBe(2);
    });

    it('should remove a user', () => {
      isolatedScope.addUserToCp({name: 'teo'});
      expect(isolatedScope.cp.users.length).toBe(2);
      isolatedScope.removeUserFromCp({name: 'teo'});
      expect(isolatedScope.cp.users.length).toBe(1);
    });

    it('should save and reformat users', () => {
      // add a user
      isolatedScope.cp.users.push(1);

      //trigger save
      isolatedScope.saveContentProvider(isolatedScope.cp);

      httpBackend.flush();

      // I'll get one as the BE is mocked, the important is to check the conversion
      expect(isolatedScope.cp.users.length).toBe(1);
      expect(typeof isolatedScope.cp.users[0]).toEqual('object');
    });
  });
});
