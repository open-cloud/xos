/**
 * © OpenCORD
 *
 * Created by teone on 5/25/16.
 */

(function () {
  'use strict';

  describe('The xos.helper module', function () {
    describe('The xosCustomValidator directive', () => {
      let element, scope, isolatedScope, rootScope, compile, form, input;
      const compileElement = (el) => {
        element = el;

        if(!scope){
          scope = rootScope.$new();
        }
        if(angular.isUndefined(element)){
          element = angular.element(`
            <form name="form">
              <input name="testInput" type="text" ng-model="value" xos-custom-validator custom-validator="validator"/>
            </form>
          `);
        }
        compile(element)(scope);
        scope.$digest();
        input = $(element).find('input');
        isolatedScope = angular.element(input).isolateScope();
        form = scope.form;
      };

      beforeEach(module('xos.helpers'));

      beforeEach(inject(function ($compile, $rootScope) {
        compile = $compile;
        rootScope = $rootScope;
      }));

      beforeEach(() => {
        scope = rootScope.$new();
        scope.validator = 'validator';
        scope.value = '';
        compileElement();
      });

      it('should bind the validator', () => {
        expect(isolatedScope.fn).toEqual('validator');
      });

      describe('given a validator function', () => {

        beforeEach(() => {
          scope = rootScope.$new();
          scope.value = '';
          scope.validator = (model) => angular.equals(model, 'test');
          spyOn(scope, 'validator').and.callThrough();
          compileElement();
        });

        it('should call the validator function on value change', () => {
          form.testInput.$setViewValue('something');
          scope.$digest();
          expect(scope.validator).toHaveBeenCalledWith('something');
          expect(scope.value).toEqual('something');
        });

        it('should set the field invalid', () => {
          form.testInput.$setViewValue('something');
          scope.$digest();
          expect(scope.validator).toHaveBeenCalledWith('something');
          expect(input).toHaveClass('ng-invalid');
          expect(input).toHaveClass('ng-invalid-custom-validation');
        });

        it('should set the field valid', () => {
          form.testInput.$setViewValue('test');
          scope.$digest();
          expect(scope.validator).toHaveBeenCalledWith('test');
          expect(input).not.toHaveClass('ng-invalid');
          expect(input).not.toHaveClass('ng-invalid-custom-validation');
        });

        describe('if the validation function return an array', () => {

          beforeEach(() => {
            scope = rootScope.$new();
            scope.value = '';
            scope.validator = (model) => {
              return ['randomTest', angular.equals(model, 'test')];
            };
            spyOn(scope, 'validator').and.callThrough();
            compileElement();
          });

          it('should set the field invalid', () => {
            form.testInput.$setViewValue('something');
            scope.$digest();
            expect(scope.validator).toHaveBeenCalledWith('something');
            expect(input).toHaveClass('ng-invalid');
            expect(input).toHaveClass('ng-invalid-random-test');
          });
        });
      });
    });
  });
})();