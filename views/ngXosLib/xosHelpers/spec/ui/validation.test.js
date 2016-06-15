/**
 * © OpenCORD
 *
 * Created by teone on 4/15/16.
 */

(function () {
  'use strict';

  let compile, element, scope;

  const compileElement = (el) => {
    element = el;

    if(!scope){
      scope = rootScope.$new();
    }
    if(angular.isUndefined(element)){
      element = angular.element('<xos-validation field="field" form="form"></xos-validation>');
    }
    compile(element)(scope);
    scope.$digest();
  }

  describe('The xos.helper module', function(){
    describe('The xos-validation component', () => {

      beforeEach(module('xos.helpers'));

      describe('when the form has no errors', () => {
        beforeEach(inject(($compile, $rootScope) => {
          compile = $compile;
          scope = $rootScope.$new();

          scope.field = {
            $error: {}
          };

          scope.form = {
            $submitted: true
          }

          compileElement();
        }));

        it('should not show an alert by default', () => {
          expect($(element).find('xos-alert > .alert')[0]).toHaveClass('ng-hide');
        });
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
          scope.field.$error[e.type] = true;
          compileElement();
          let alert = $(element).find('xos-alert > .alert')[i];
          expect(alert).not.toHaveClass('ng-hide');
          expect(alert).toHaveText(e.message);
        });
      });
    });
  });
})();