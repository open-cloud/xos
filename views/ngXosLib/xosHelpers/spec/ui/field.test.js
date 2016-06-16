/**
 * © OpenCORD
 *
 * Created by teone on 5/25/16.
 */

(function () {
  'use strict';

  describe('The xos.helper module', function(){

    describe('The xosField component', () => {
      let element, scope, isolatedScope, rootScope, compile;
      const compileElement = (el) => {
        element = el;

        if(!scope){
          scope = rootScope.$new();
        }
        if(angular.isUndefined(element)){
          element = angular.element('<xos-field name="name" field="field" ng-model="ngModel"></xos-field>');
        }
        compile(element)(scope);
        scope.$digest();
        isolatedScope = element.isolateScope().vm;
      };

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

      it('should throw an error if no field type is passed', inject(($compile, $rootScope) => {
        function errorFunctionWrapper(){
          // setup the parent scope
          scope = $rootScope.$new();
          scope.name = 'label';
          scope.ngModel = 1;
          scope.field = {label: 'Label:'}
          compileElement();
        }
        expect(errorFunctionWrapper).toThrow(new Error('[xosField] Please provide a type in the field definition'));
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
            validators: {
              custom: 'fake'
            }
          };
          scope.ngModel = 'label';
          compileElement();
        });

        it('should print a text field', () => {
          expect($(element).find('[name="label"]')).toHaveAttr('type', 'text');
        });

        it('should attach the custom validator directive', () => {
          let input = $(element).find('[name="label"]');
          expect(input).toHaveAttr('xos-custom-validator');
          expect(input).toHaveAttr('custom-validator', 'vm.field.validators.custom || null');
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
          scope.ngModel = 0;
          compileElement();
        });

        it('No of select elements', () => {
          expect($(element).find('select').children('option').length).toEqual(2);
        });

        it('should show the selected value', () => {
          var elem =  angular.element($(element).find('select').children('option')[0]);
          expect(elem.text()).toEqual('---Site---');
          expect(elem).toHaveAttr('selected');
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
          setFalse= $(element).find('.boolean-field > a:first-child');
          setTrue = $(element).find('.boolean-field > a:last-child');
        });

        it('should print two buttons', () => {
          expect($(element).find('.boolean-field > a').length).toEqual(2)
        });

        it('should change value to false', () => {
          expect(isolatedScope.ngModel).toEqual(true);
          clickElement(setFalse[0]);
          expect(isolatedScope.ngModel).toEqual(false);
        });

        it('should change value to true', () => {
          isolatedScope.ngModel = false;
          scope.$apply();
          expect(isolatedScope.ngModel).toEqual(false);
          clickElement(setTrue[0]);
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
          expect($(element).find('.boolean-field > a').length).toEqual(2);
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
            expect($(element).find('.panel.object-field')).not.toExist()
          });

          describe('but field is configured', () => {
            beforeEach(() => {
              scope.field.properties = {
                foo: {
                  label: 'FooLabel:',
                  type: 'string',
                  validators: {
                    required: true
                  }
                },
                bar: {
                  type: 'number'
                }
              };
              compileElement();
            });
            it('should render panel and configured fields', () => {
              expect($(element).find('.panel.object-field')).toExist();
              expect($(element).find('input[name="foo"]').parent().find('label').text()).toBe('FooLabel:');
              expect($(element).find('input[name="foo"]')).toHaveAttr('type', 'string');
              expect($(element).find('input[name="foo"]')).toHaveAttr('required');

              expect($(element).find('input[name="bar"]').parent().find('label').text()).toBe('Bar:');
              expect($(element).find('input[name="bar"]')).toHaveAttr('type', 'number');

            });
          });
        });
      });

      describe('when validation options are passed', () => {
        let input;
        describe('given a a text field', () => {
          beforeEach(() => {
            scope.field = {
              label: 'Label',
              type: 'text',
              validators: {
                minlength: 10,
                maxlength: 15,
                required: true
              }
            };

            scope.$digest();
            input = $(element).find('input');
          });

          it('should validate required', () => {
            scope.ngModel= null;
            scope.$digest();
            expect(input).toHaveClass('ng-invalid-required');

            scope.ngModel= 'not too short';
            scope.$digest();
            expect(input).not.toHaveClass('ng-invalid-required');
            expect(input).not.toHaveClass('ng-invalid');
          });

          it('should validate minlength', () => {
            scope.ngModel= 'short';
            scope.$digest();
            expect(input).toHaveClass('ng-invalid-minlength');

            scope.ngModel= 'not too short';
            scope.$digest();
            expect(input).not.toHaveClass('ng-invalid-minlength');
            expect(input).not.toHaveClass('ng-invalid');
          });

          it('should validate maxlength', () => {
            scope.ngModel= 'this is definitely too long!!';
            scope.$digest();
            expect(input).toHaveClass('ng-invalid-maxlength');

            scope.ngModel= 'not too short';
            scope.$digest();
            expect(input).not.toHaveClass('ng-invalid-maxlength');
            expect(input).not.toHaveClass('ng-invalid');
          });
        });
      });
    });
  });
})();