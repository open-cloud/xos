'use strict';

describe('The xos.helper module', () => {
  
  var app, httpProvider;

  beforeEach(module('xos.helpers'));
  beforeEach(function(){
    module(function($httpProvider){
      httpProvider = $httpProvider;
    });
  });



  it('should set SetCSRFToken interceptor', inject(($http) => {
    expect(httpProvider.interceptors).toContain('SetCSRFToken');
  }));

});