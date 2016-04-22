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

      let availableErrors = [
        {
          type: 'required',
          message: 'Field required'
        },
        {
          type: 'email',
          message: 'This is not a valid email'
        },
        {
          type: 'minlength',
          message: 'Too short'
        },
        {
          type: 'maxlength',
          message: 'Too long'
        },
        {
          type: 'custom',
          message: 'Field invalid'
        },
      ];

      // use a loop to generate similar test
      availableErrors.forEach((e, i) => {
        it(`should show an alert for ${e.type} errors`, () => {
          scope.errors[e.type] = true;
          scope.$digest();
          let alert = $(element).find('xos-alert > .alert')[i];
          expect(alert).not.toHaveClass('ng-hide');
          expect(alert).toHaveText(e.message);
        });
      });
    });
  });
})();