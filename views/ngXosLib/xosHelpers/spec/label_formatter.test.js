(function () {
  'use strict';

  describe('The xos.helper module', function(){
    describe('The label formatter service', () => {

      let service;

      // load the application module
      beforeEach(module('xos.helpers'));

      // inject the cartService
      beforeEach(inject(function (_LabelFormatter_) {
        // The injector unwraps the underscores (_) from around the parameter names when matching
        service = _LabelFormatter_;
      }));

      it('should replace underscores in a string', () => {
        expect(service._formatByUnderscore('my_test')).toEqual('my test');
        expect(service._formatByUnderscore('_test')).toEqual('test');
      });

      it('should split a camel case string', () => {
        expect(service._formatByUppercase('myTest')).toEqual('my test');
      });

      it('should capitalize a string', () => {
        expect(service._capitalize('my test')).toEqual('My test');
      });

      it('should format an object property to a label', () => {
        expect(service.format('myWeird_String')).toEqual('My weird string:');
      });

      it('should not add column if already present', () => {
        expect(service.format('myWeird_String:')).toEqual('My weird string:');
      });

    });
  });

})();