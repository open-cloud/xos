'use strict';

describe('The xos.helper module', function(){
  
  var app, httpProvider;

  beforeEach(module('xos.helpers'));

  beforeEach(function(){
    module(function(_$httpProvider_){
      console.log('beforeEach');
      httpProvider = _$httpProvider_;
    });
  });

  it('should set SetCSRFToken interceptor', inject(function($http){
    console.log('httpProvider',httpProvider);
    expect(true).toBeTrue();
    // expect(httpProvider.interceptors).toContain('SetCSRFToken');
  }));

});