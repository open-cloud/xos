/**
 * © OpenCORD
 *
 * Created by teone on 4/15/16.
 */

(function () {
  'use strict';

  describe('The xos.helper module', function(){
    describe('The xos-validation component', () => {

      let element, scope, isolatedScope;

      beforeEach(module('xos.helpers'));

      beforeEach(inject(($compile, $rootScope) => {

        scope = $rootScope.$new();

        scope.errors = {};

        element = angular.element(`<xos-validation errors="errors"></xos-validation>`);
        $compile(element)(scope);
        scope.$digest();
        isolatedScope = element.isolateScope().vm;
      }));

      it('should not show an alert', () => {
        expect($(element).find('xos-alert > .alert')[0]).toHaveClass('ng-hide');
      });

      it('should show an alert', () => {
        scope.errors.email = true;
        scope.$digest();
        expect($(element).find('xos-alert > .alert')[0]).not.toHaveClass('ng-hide');
      });
    });
  });
})();