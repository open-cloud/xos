/**
 * © OpenCORD
 *
 * Created by teone on 5/25/16.
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
        'created'
      ];

      let modelField = {
        id: {},
        name: {},
        mail: {},
        active: {},
        created: {}
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
        id: {
          label: 'Id',
          type: 'number',
          validators: {
            required: true
          },
          hint: ''
        },
        custom: {
          label: 'Custom Label',
          type: 'number',
          validators: {},
          hint: 'Test Hint'
        }
      };

      let formObject = {
        id: {
          label: 'Id:',
          type: 'number',
          validators: {
            required: true
          },
          hint: ''
        },
        name: {
          label: 'Name:',
          type: 'text',
          validators: {},
          hint: ''
        },
        mail: {
          label: 'Mail:',
          type: 'email',
          validators: {},
          hint: ''
        },
        active: {
          label: 'Active:',
          type: 'boolean',
          validators: {},
          hint: ''
        },
        created: {
          label: 'Created:',
          type: 'date',
          validators: {},
          hint: ''
        },
        custom: {
          label: 'Custom Label:',
          type: 'number',
          validators: {},
          hint: 'Test Hint'
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
        it('should return text', () => {
          expect(service._getFieldFormat('a random text')).toEqual('text');
          expect(service._getFieldFormat(null)).toEqual('text');
          expect(service._getFieldFormat('1')).toEqual('text');
        });
        it('should return mail', () => {
          expect(service._getFieldFormat('test@onlab.us')).toEqual('email');
        });
        it('should return number', () => {
          expect(service._getFieldFormat(1)).toEqual('number');
        });
        it('should return boolean', () => {
          expect(service._getFieldFormat(false)).toEqual('boolean');
          expect(service._getFieldFormat(true)).toEqual('boolean');
        });

        it('should return date', () => {
          expect(service._getFieldFormat('2016-04-19T23:09:1092Z')).toEqual('text');
          expect(service._getFieldFormat(new Date())).toEqual('date');
          expect(service._getFieldFormat('2016-04-19T23:09:10.208092Z')).toEqual('date');
        });

        it('should return array', () => {
          expect(service._getFieldFormat([])).toEqual('array');
          expect(service._getFieldFormat(['a', 'b'])).toEqual('array');
        });

        it('should return object', () => {
          expect(service._getFieldFormat({})).toEqual('object');
          expect(service._getFieldFormat({foo: 'bar'})).toEqual('object');
        });
      });

      describe('the parseModelField mehtod', () => {
        it('should convert the fields array in an empty form object', () => {
          expect(service.parseModelField(fields)).toEqual(modelField);
        });

        xit('should handle nested config', () => {
          
        });
      });

      describe('when modelField are provided', () => {
        it('should combine modelField and customField in a form object', () => {
          const form = service.buildFormStructure(modelField, customField, model);
          expect(form).toEqual(formObject);
        });

        it('should override modelField properties whith customField properties', () => {
          const customFieldOverride = {
            id: {
              hint: 'something',
              type: 'select',
              options: [
                {id: 1, label: 'one'},
                {id: 2, label: 'two'}
              ],
              validators: {
                required: true
              }
            }
          };
          const form = service.buildFormStructure({id: {}}, customFieldOverride, model);
          
          expect(form).toEqual({
            id: {
              label: 'Id:',
              validators: {required: true},
              hint: customFieldOverride.id.hint,
              type: customFieldOverride.id.type,
              options: customFieldOverride.id.options
            }
          });
        });
      });

      describe('when model field is an empty array', () => {
        let empty_modelField = {
          // 5: {}
        };
        let empty_customFields = {
          id: {
            label: 'Id',
            type: 'number'
          },
          name: {
            label: 'Name',
            type: 'text'
          },
          mail: {
            label: 'Mail',
            type: 'email'
          },
          active: {
            label: 'Active',
            type: 'boolean'
          },
          created: {
            label: 'Created',
            type: 'date'
          },
          custom: {
            label: 'Custom Label',
            type: 'number',
            hint: 'Test Hint'
          },
          select: {
            label: 'Select Label',
            type: 'select',
            hint: 'Select Hint',
            options: [
              {id: 1, label: 'something'}
            ]
          },
          object: {
            label: 'Object Label',
            type: 'object',
            hint: 'Object Hint',
            properties: {
              foo: {
                type: 'string',
                label: 'FooLabel',
                validators: {
                  required: true
                }
              },
              bar: {
                type: 'number'
              }
            }
          }
        };

        let empty_formObject = {
          id: {
            label: 'Id:',
            type: 'number',
            validators: {},
            hint: ''
          },
          name: {
            label: 'Name:',
            type: 'text',
            validators: {},
            hint: ''
          },
          mail: {
            label: 'Mail:',
            type: 'email',
            validators: {},
            hint: ''
          },
          active: {
            label: 'Active:',
            type: 'boolean',
            validators: {},
            hint: ''
          },
          created: {
            label: 'Created:',
            type: 'date',
            validators: {},
            hint: ''
          },
          custom: {
            label: 'Custom Label:',
            type: 'number',
            validators: {},
            hint: 'Test Hint'
          },
          select: {
            label: 'Select Label:',
            type: 'select',
            hint: 'Select Hint',
            validators: {},
            options: [
              {id: 1, label: 'something'}
            ]
          },
          object: {
            label: 'Object Label:',
            type: 'object',
            hint: 'Object Hint',
            validators: {},
            properties: {
              foo: {
                type: 'string',
                label: 'FooLabel',
                validators: {
                  required: true
                }
              },
              bar: {
                type: 'number'
              }
            }
          }
        };

        let empty_model = {5: 'Nan'}

        it('should create a form object', () => {
          let res = service.buildFormStructure(empty_modelField, empty_customFields, empty_model);
          expect(res.id).toEqual(empty_formObject.id);
          expect(res.name).toEqual(empty_formObject.name);
          expect(res.mail).toEqual(empty_formObject.mail);
          expect(res.active).toEqual(empty_formObject.active);
          expect(res.created).toEqual(empty_formObject.created);
          expect(res.custom).toEqual(empty_formObject.custom);
          expect(res.select).toEqual(empty_formObject.select);
          expect(res.object).toEqual(empty_formObject.object);
          expect(res).toEqual(empty_formObject);
        });
      });
    });
  });
})();