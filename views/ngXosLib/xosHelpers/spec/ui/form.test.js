/**
 * © OpenCORD
 *
 * Created by teone on 4/18/16.
 */

(function () {
  'use strict';

  describe('The xos.helper module', function(){

    describe('The XosFormHelper service', () => {
      let service;

      let fields = [
        'id',
        'name',
        'mail',
        'active',
        'created',
        'custom'
      ];

      let modelField = {
        id: {},
        name: {},
        mail: {},
        active: {},
        created: {},
        custom: {}
      };

      let model = {
        id: 1,
        name: 'test',
        mail: 'test@onlab.us',
        active: true,
        created: '2016-04-18T23:44:16.883181Z',
        custom: 'MyCustomValue'
      };

      let customField = {
        custom: {
          label: 'Custom Label',
          type: 'number',
          validators: {}
        }
      };

      let formObject = {
        id: {
          label: 'Id:',
          type: 'number',
          validators: {}
        },
        name: {
          label: 'Name:',
          type: 'string',
          validators: {}
        },
        mail: {
          label: 'Mail:',
          type: 'email',
          validators: {}
        },
        active: {
          label: 'Active:',
          type: 'boolean',
          validators: {}
        },
        created: {
          label: 'Created:',
          type: 'date',
          validators: {}
        },
        custom: {
          label: 'Custom Label:',
          type: 'number',
          validators: {}
        }
      };

      // load the application module
      beforeEach(module('xos.helpers'));

      // inject the cartService
      beforeEach(inject(function (_XosFormHelpers_) {
        // The injector unwraps the underscores (_) from around the parameter names when matching
        service = _XosFormHelpers_;
      }));

      describe('the _isEmail method', () => {
        it('should return true', () => {
          expect(service._isEmail('test@onlab.us')).toEqual(true);
        });
        it('should return false', () => {
          expect(service._isEmail('testonlab.us')).toEqual(false);
          expect(service._isEmail('test@onlab')).toEqual(false);
        });
      });

      describe('the _getFieldFormat method', () => {
        it('should return string', () => {
          expect(service._getFieldFormat('string')).toEqual('string');
        });
        it('should return mail', () => {
          expect(service._getFieldFormat('test@onlab.us')).toEqual('email');
        });
        it('should return number', () => {
          expect(service._getFieldFormat(1)).toEqual('number');
          expect(service._getFieldFormat('1')).toEqual('number');
        });
        it('should return boolean', () => {
          expect(service._getFieldFormat(false)).toEqual('boolean');
          expect(service._getFieldFormat(true)).toEqual('boolean');
        });

        it('should return date', () => {
          expect(service._getFieldFormat('2016-04-19T23:09:1092Z')).toEqual('string');
          expect(service._getFieldFormat(new Date())).toEqual('date');
          expect(service._getFieldFormat('2016-04-19T23:09:10.208092Z')).toEqual('date');
        });
      });

      it('should convert the fields array in an empty form object', () => {
        expect(service.parseModelField(fields)).toEqual(modelField);
      });

      it('should combine modelField and customField in a form object', () => {
        expect(service.buildFormStructure(modelField, customField, model)).toEqual(formObject);
      });
    });

    describe('The xos-form component', () => {

      let element, scope, isolatedScope;

      beforeEach(module('xos.helpers'));

      it('should throw an error if no config is specified', inject(($compile, $rootScope) => {
        function errorFunctionWrapper(){
          $compile(angular.element('<xos-form></xos-form>'))($rootScope);
          $rootScope.$digest();
        }
        expect(errorFunctionWrapper).toThrow(new Error('[xosForm] Please provide a configuration via the "config" attribute'));
      }));

      it('should throw an error if no actions is specified', inject(($compile, $rootScope) => {
        function errorFunctionWrapper(){
          let scope = $rootScope.$new();
          scope.config = 'green';
          $compile(angular.element('<xos-form config="config"></xos-form>'))(scope);
          $rootScope.$digest();
        }
        expect(errorFunctionWrapper).toThrow(new Error('[xosForm] Please provide an action list in the configuration'));
      }));

      describe('when correctly configured', () => {
        
        let cb = jasmine.createSpy('callback');

        beforeEach(inject(($compile, $rootScope) => {


          scope = $rootScope.$new();

          scope.config = {
            exclude: ['excludedField'],
            actions: [
              {
                label: 'Save',
                icon: 'ok', // refers to bootstraps glyphicon
                cb: cb,
                class: 'success'
              }
            ],
            fields: {
              first_name: {
                label: 'Custom Label'
              }
            }
          };

          scope.model = {
            id: 1,
            first_name: 'Jhon',
            last_name: 'Snow',
            age: 25,
            email: 'test@onlab.us',
            birthDate: '2016-04-18T23:44:16.883181Z',
            enabled: true,
            role: 'user', //select
            a_permissions: [

            ],
            o_permissions: {

            }
          };

          element = angular.element(`<xos-form config="config" ng-model="model"></xos-form>`);
          $compile(element)(scope);
          scope.$digest();
          isolatedScope = element.isolateScope().vm;
        }));

        it('should add excluded properties to the list', () => {
          let expected = ['id', 'validators', 'created', 'updated', 'deleted', 'backend_status', 'excludedField'];
          expect(isolatedScope.excludedField).toEqual(expected);
        });

        it('should render 8 input field', () => {
          // boolean are in the form model, but are not input
          expect(Object.keys(isolatedScope.formField).length).toEqual(9);
          var field = element[0].getElementsByTagName('input');
          expect(field.length).toEqual(8);
        });

        it('should render 1 boolean field', () => {
          expect($(element).find('.boolean-field > button').length).toEqual(2)
        });

        it('when clicking on action should invoke callback', () => {
          var link = $(element).find('[role="button"]');
          link.click();
          expect(cb).toHaveBeenCalledWith(scope.model);
        });

        it('should set a custom label', () => {
          let nameField = element[0].getElementsByClassName('form-group')[0];
          let label = angular.element(nameField.getElementsByTagName('label')[0]).text()
          expect(label).toEqual('Custom Label:');
        });

        it('should use the correct input type', () => {
          expect($(element).find('[name="age"]')).toHaveAttr('type', 'number');
          expect($(element).find('[name="birthDate"]')).toHaveAttr('type', 'date');
          expect($(element).find('[name="email"]')).toHaveAttr('type', 'email');
        });

        describe('the boolean field', () => {

          let setFalse, setTrue;

          beforeEach(() => {
            setFalse= $(element).find('.boolean-field > button:first-child');
            setTrue = $(element).find('.boolean-field > button:last-child');
          });

          it('should change value to false', () => {
            expect(isolatedScope.ngModel.enabled).toEqual(true);
            setFalse.click()
            expect(isolatedScope.ngModel.enabled).toEqual(false);
          });

          it('should change value to false', () => {
            isolatedScope.ngModel.enabled = false;
            scope.$apply();
            expect(isolatedScope.ngModel.enabled).toEqual(false);
            setTrue.click()
            expect(isolatedScope.ngModel.enabled).toEqual(true);
          });
        });
      });
    });
  });
})();
