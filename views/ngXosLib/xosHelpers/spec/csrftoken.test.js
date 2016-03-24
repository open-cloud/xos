'use strict';
describe('The xos.helper module', function(){
  var SetCSRFToken, httpProviderObj;

  //beforeEach(module('xos.helpers'));
  //
  //beforeEach(inject(function($httpProvider){
  //  httpProviderObj = $httpProvider;
  //}));
  //
  //beforeEach(inject(function(_SetCSRFToken_){
  //  console.log('inject csrf');
  //  SetCSRFToken = _SetCSRFToken_;
  //}));

  beforeEach(function() {
    module('xos.helpers', function ($httpProvider) {
      //save our interceptor
      httpProviderObj = $httpProvider;
    });

    inject(function (_SetCSRFToken_) {
      SetCSRFToken = _SetCSRFToken_;
    })
  });

  it('should exist', () => {
    expect(SetCSRFToken).toBeDefined();
  });
  
  it('should set SetCSRFToken interceptor', () => {
    expect(httpProviderObj).toBeDefined();
    expect(httpProviderObj.interceptors).toContain('SetCSRFToken');
  });

});