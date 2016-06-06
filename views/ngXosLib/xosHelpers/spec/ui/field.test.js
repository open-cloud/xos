/**
 * © OpenCORD
 *
 * Created by teone on 5/25/16.
 */

(function () {
  'use strict';

  let element, scope, isolatedScope, rootScope, compile;
  const compileElement = (el) => {
    element = el;

    if(!scope){
      scope = rootScope.$new();
    }
    if(!angular.isDefined(element)){
      element = angular.element('<xos-field name="name" field="field" ng-model="ngModel"></xos-field>');
    }
    compile(element)(scope);
    scope.$digest();
    isolatedScope = element.isolateScope().vm;
  }

  describe('The xos.helper module', function(){

    describe('The xosField component', () => {

      beforeEach(module('xos.helpers'));

      beforeEach(inject(function ($compile, $rootScope) {
        compile = $compile;
        rootScope = $rootScope;
      }));

      it('should throw an error if no name is passed', inject(($compile, $rootScope) => {
        function errorFunctionWrapper(){
          // setup the parent scope
          scope = $rootScope.$new();
          scope.field = {
            label: 'Label',
            type: 'number',
            validators: {}
          };
          scope.ngModel = 1;
          compileElement();
        }
        expect(errorFunctionWrapper).toThrow(new Error('[xosField] Please provide a field name'));
      }));

      it('should throw an error if no field definition is passed', inject(($compile, $rootScope) => {
        function errorFunctionWrapper(){
          // setup the parent scope
          scope = $rootScope.$new();
          scope.name = 'label';
          scope.ngModel = 1;
          compileElement();
        }
        expect(errorFunctionWrapper).toThrow(new Error('[xosField] Please provide a field definition'));
      }));

      it('should throw an error if no field model is passed', inject(($compile, $rootScope) => {
        function errorFunctionWrapper(){
          // setup the parent scope
          scope = $rootScope.$new();
          scope.name = 'label';
          scope.field = {
            label: 'Label',
            type: 'number',
            validators: {}
          };
          compileElement(angular.element('<xos-field name="name" field="field"></xos-field>'));
        }
        expect(errorFunctionWrapper).toThrow(new Error('[xosField] Please provide an ng-model'));
      }));

      describe('when a text input is passed', () => {
        beforeEach(() => {
          scope = rootScope.$new();
          scope.name = 'label';
          scope.field = {
            label: 'Label',
            type: 'text',
            validators: {}
          };
          scope.ngModel = 'label';
          compileElement();
        });

        it('should print a text field', () => {
          expect($(element).find('[name="label"]')).toHaveAttr('type', 'text');
        });
      });




      describe('when a option is selected in dropdown', () => {
        beforeEach(() => {
          scope = rootScope.$new();
          scope.name = 'label';
          scope.field = {
            label: 'Label',
            type: 'select',
            validators: {},
            options: [
              {
                id: 0,
                label: '---Site---'
              },
              {
                id: 1,
                label: '---Site1---'
              }
            ]
          };
          scope.ngModel = 'label';
          compileElement();
        });

        it('No of select elements', () => {
          expect($(element).find('select').children('option').length).toEqual(3);
        });

        it('should show a selected value', () => {
          var elem =  angular.element($(element).find('select').children('option')[1]);
          expect(elem.text()).toEqual('---Site---');
        });
      });

      describe('when a number input is passed', () => {
        beforeEach(() => {
          scope = rootScope.$new();
          scope.name = 'label';
          scope.field = {
            label: 'Label',
            type: 'number',
            validators: {}
          };
          scope.ngModel = 10;
          compileElement();
        });

        it('should print a number field', () => {
          expect($(element).find('[name="label"]')).toHaveAttr('type', 'number');
        });
      });

      describe('when a boolean input is passed', () => {
        beforeEach(() => {
          scope = rootScope.$new();
          scope.name = 'label';
          scope.field = {
            label: 'Label',
            type: 'boolean',
            validators: {}
          };
          scope.ngModel = true;
          compileElement();
        });

        let setFalse, setTrue;

        beforeEach(() => {
          setFalse= $(element).find('.boolean-field > button:first-child');
          setTrue = $(element).find('.boolean-field > button:last-child');
        });

        it('should print two buttons', () => {
          expect($(element).find('.boolean-field > button').length).toEqual(2)
        });

        it('should change value to false', () => {
          expect(isolatedScope.ngModel).toEqual(true);
          setFalse.click()
          expect(isolatedScope.ngModel).toEqual(false);
        });

        it('should change value to true', () => {
          isolatedScope.ngModel = false;
          scope.$apply();
          expect(isolatedScope.ngModel).toEqual(false);
          setTrue.click()
          expect(isolatedScope.ngModel).toEqual(true);
        });
      });

      describe('when an object input is passed', () => {
        beforeEach(() => {
          scope = rootScope.$new();
          scope.name = 'label';
          scope.field = {
            label: 'Label',
            type: 'object',
            validators: {}
          };
          scope.ngModel = {
            baz: true,
            foo: 'bar',
            foz: 1,
          };
          compileElement();
        });

        it('should print a panel to contain object property field', () => {
          expect($(element).find('.panel.object-field')).toExist()
        });

        it('should print the right input type for each property', () => {
          expect($(element).find('input').length).toBe(2);
          expect($(element).find('.boolean-field > button').length).toEqual(2);
        });

        it('should format labels', () => {
          expect($(element).find('input[name="foo"]').parent().find('label').text()).toBe('Foo:');
        });

        describe('and the model is empty', () => {
          beforeEach(() => {
            scope.ngModel = {
            };
            compileElement();
          });

          it('should not print the panel', () => {
            // console.log($(element).find('.panel.object-field'));
            expect($(element).find('.panel.object-field')).not.toExist()
          });
        });
      });
    });
  });
})();