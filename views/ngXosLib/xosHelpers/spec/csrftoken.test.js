'use strict';
describe('The xos.helper module', function(){
  var SetCSRFToken, httpProviderObj, httpBackend, http, cookies;

  const fakeToken = 'aiuhsnds98234ndASd';

  beforeEach(function() {
    module(
      'xos.helpers',
      function ($httpProvider) {
        //save our interceptor
        httpProviderObj = $httpProvider;
      }
    );

    inject(function (_SetCSRFToken_, _$httpBackend_, _$http_, _$cookies_) {
      SetCSRFToken = _SetCSRFToken_;
      httpBackend = _$httpBackend_;
      http = _$http_;
      cookies = _$cookies_

      // mocking $cookie service
      spyOn(cookies, 'get').and.returnValue(fakeToken);
    });

  });

  describe('the SetCSRFToken', () => {
    it('should exist', () => {
      expect(SetCSRFToken).toBeDefined();
    });

    it('should attach token the request', (done) => {
      httpBackend.when('POST', 'http://example.com', null, function(headers) {
        expect(headers['X-CSRFToken']).toBe(fakeToken);
        done();
        return headers;
      }).respond(200, {name: 'example' });

      http.post('http://example.com');

      httpBackend.flush();
    });
  });
  
  it('should set SetCSRFToken interceptor', () => {
    expect(httpProviderObj).toBeDefined();
    expect(httpProviderObj.interceptors).toContain('SetCSRFToken');
  });

});