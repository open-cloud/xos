/**
 * © OpenCORD
 *
 * Created by teone on 4/18/16.
 */

(function () {
  'use strict';

  let element, scope, isolatedScope, rootScope, compile;

  const compileElement = () => {

    if(!scope){
      scope = rootScope.$new();
    }

    element = angular.element(`<xos-form config="config" ng-model="model"></xos-form>`);
    compile(element)(scope);
    scope.$digest();
    isolatedScope = element.isolateScope().vm;
  }

  describe('The xos.helper module', function(){

    describe('The xos-form component', () => {


      beforeEach(module('xos.helpers'));

      beforeEach(inject(($compile, $rootScope) => {
        rootScope = $rootScope;
        compile = $compile;
      }));

      it('should throw an error if no config is specified', () => {
        function errorFunctionWrapper(){
          compileElement();
        }
        expect(errorFunctionWrapper).toThrow(new Error('[xosForm] Please provide a configuration via the "config" attribute'));
      });

      it('should throw an error if no actions is specified', () => {
        function errorFunctionWrapper(){
          scope = rootScope.$new();
          scope.config = 'green';
          compileElement();
        }
        expect(errorFunctionWrapper).toThrow(new Error('[xosForm] Please provide an action list in the configuration'));
      });

      describe('when correctly configured', () => {
        
        let cb = jasmine.createSpy('callback');

        beforeEach(inject(($rootScope) => {

          scope = $rootScope.$new();

          scope.config = {
            exclude: ['excludedField'],
            formName: 'testForm',
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
            object_field: {
              string: 'bar',
              number: 1,
              email: 'teo@onlab.us'
            }
          };

          compileElement();
        }));

        it('should add excluded properties to the list', () => {
          let expected = ['id', 'validators', 'created', 'updated', 'deleted', 'backend_status', 'excludedField'];
          expect(isolatedScope.excludedField).toEqual(expected);
        });

        it('should render 10 input field', () => {
          // boolean are in the form model, but are not input
          expect(Object.keys(isolatedScope.formField).length).toEqual(9);
          var field = element[0].getElementsByTagName('input');
          expect(field.length).toEqual(10);
        });

        it('should render 1 boolean field', () => {
          expect($(element).find('.boolean-field > a').length).toEqual(2)
        });

        it('when clicking on action should invoke callback', () => {
          var link = $(element).find('[role="button"]');
          //console.log(link);
          link.click();
          // TODO : Check correct parameters
          expect(cb).toHaveBeenCalled();

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

        xdescribe('the boolean field test', () => {

          let setFalse, setTrue;

          beforeEach(() => {
            setFalse= $(element).find('.boolean-field > button:first-child');
            setTrue = $(element).find('.boolean-field > button:last-child');
          });

          it('should change value to false', () => {
            expect(isolatedScope.ngModel.enabled).toEqual(true);
            setFalse.click();
            expect(isolatedScope.ngModel.enabled).toEqual(false);
          });

          it('should change value to true', () => {
            isolatedScope.ngModel.enabled = false;
            scope.$apply();
            expect(isolatedScope.ngModel.enabled).toEqual(false);
            setTrue.click()
            expect(isolatedScope.ngModel.enabled).toEqual(true);
          });
        });

        describe('when a deep model is passed', () => {

          beforeEach(inject(($rootScope) => {

            scope = $rootScope.$new();

            scope.config = {
              exclude: ['excludedField'],
              formName: 'testForm',
              actions: [
                {
                  label: 'Save',
                  icon: 'ok', // refers to bootstraps glyphicon
                  cb: cb,
                  class: 'success'
                }
              ],
              fields: {
                object_field: {
                  field_one: {
                    label: 'Custom Label'
                  }
                }
              }
            };

            scope.model = {
              object_field: {
                field_one: 'bar',
                number: 1,
                email: 'teo@onlab.us'
              }
            };

            compileElement();
          }));

          it('should print nested field', () => {
            expect($(element).find('input').length).toBe(3);
          });

          xit('should configure nested fields', () => {
            let custom_label = $(element).find('input[name=field_one]').parent().find('label');
            expect(custom_label.text()).toBe('Custom Label');
          });
        });
      });
      describe('when correctly configured for feedback', () => {

        let fb = jasmine.createSpy('feedback').and.callFake(function(statusFlag) {
          if(statusFlag){
            scope.config.feedback.show = true;
            scope.config.feedback.message = 'Form Submitted';
            scope.config.feedback.type = 'success';
          }
          else {
            scope.config.feedback.show = true;
            scope.config.feedback.message = 'Error';
            scope.config.feedback.type = 'danger';

          }
        });

        beforeEach(()=> {
          scope = rootScope.$new();
          scope.config =
          {

            feedback: {
              show: false,
              message: 'Form submitted successfully !!!',
              type: 'success'
            },
            actions: [
              {
                label: 'Save',
                icon: 'ok', // refers to bootstraps glyphicon
                cb: () => {},
                class: 'success'
              }
            ]
          };
          scope.model={};
          compileElement();
        });

        it('should not show feedback when loaded', () => {
          expect($(element).find('xos-alert > div')).toHaveClass('alert alert-success ng-hide');
        });

        it('should show a success feedback', () => {
          fb(true);
          scope.$digest();
          expect(isolatedScope.config.feedback.type).toEqual('success');
          expect(fb).toHaveBeenCalledWith(true);
          expect($(element).find('xos-alert > div')).toHaveClass('alert alert-success');
        });

        it('should show an error feedback', function() {
          fb(false);
          scope.$digest();
          expect(isolatedScope.config.feedback.type).toEqual('danger');
          expect(fb).toHaveBeenCalledWith(false);
          expect($(element).find('xos-alert > div')).toHaveClass('alert alert-danger');
        });
      });

    });
  });
})();
