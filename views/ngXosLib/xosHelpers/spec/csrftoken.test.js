'use strict';
describe('The xos.helper module', function(){
  var SetCSRFToken, httpProviderObj;

  beforeEach(module('xos.helpers'));

  beforeEach(module(function(_$httpProvider_){
    httpProviderObj = _$httpProvider_;
  }));

  beforeEach(angular.mock.inject(function(_SetCSRFToken_){
    SetCSRFToken = _SetCSRFToken_;
  }));

  it('should exist', () => {
    expect(SetCSRFToken).toBeDefined();
  });
  
  xit('should set SetCSRFToken interceptor', () => {
    expect(httpProviderObj).toBeDefined();
    expect(httpProviderObj.interceptors).toContain('SetCSRFToken');
  });

});