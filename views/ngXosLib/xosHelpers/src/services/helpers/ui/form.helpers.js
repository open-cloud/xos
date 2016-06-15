(function () {
  
  angular.module('xos.uiComponents')

  /**
  * @ngdoc service
  * @name xos.uiComponents.XosFormHelpers
  * @requires xos.uiComponents.LabelFormatter
  * @requires xos.helpers._
  **/

  .service('XosFormHelpers', function(_, LabelFormatter){

    /**
    * @ngdoc method
    * @name xos.uiComponents.XosFormHelpers#_isEmail
    * @methodOf xos.uiComponents.XosFormHelpers
    * @description
    * Return true if the string is an email address
    * @param {string} text The string to be evaluated
    * @returns {boolean} If the string match an email format
    **/


    this._isEmail = (text) => {
      var re = /(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))/;
      return re.test(text);
    };

    /**
    * @ngdoc method
    * @name xos.uiComponents.XosFormHelpers#_getFieldFormat
    * @methodOf xos.uiComponents.XosFormHelpers
    * @description
    * Return the type of the input
    * @param {mixed} value The data to be evaluated
    * @returns {string} The type of the input
    **/

    this._getFieldFormat = (value) => {

      if(angular.isArray(value)){
        return 'array';
      }

      // check if is date
      if (_.isDate(value) || (!Number.isNaN(Date.parse(value)) && new Date(value).getTime() > 631180800000)){
        return 'date';
      }

      // check if is boolean
      // isNaN(false) = false, false is a number (0), true is a number (1)
      if(typeof value  === 'boolean'){
        return 'boolean';
      }

      // check if a string is an email
      if(this._isEmail(value)){
        return 'email';
      }

      // if null return string
      if(angular.isString(value) || value === null){
        return 'text';
      }

      return typeof value;
    };

    /**
    * @ngdoc method
    * @name xos.uiComponents.XosFormHelpers#buildFormStructure
    * @methodOf xos.uiComponents.XosFormHelpers
    * @description
    * Return the type of the input
    * @param {object} modelField An object containing one property for each field of the model
    * @param {object} customField An object containing one property for each field custom field
    * @param {object} model The actual model on wich build the form structure (it is used to determine the type of the input)
    * @returns {object} An object describing the form structure in the form of:
    * ```
    * {
    *   'field-name': {
    *     label: 'Label',
    *     type: 'number', //typeof field
    *     validators: {}, // see xosForm for more details
    *     hint: 'A Custom hint for the field'
    *   }
    * }
    * ```
    **/

    this.buildFormStructure = (modelField, customField, model) => {

      modelField = angular.extend(modelField, customField);
      customField = customField || {};

      return _.reduce(Object.keys(modelField), (form, f) => {

        form[f] = {
          label: (customField[f] && customField[f].label) ? `${customField[f].label}:` : LabelFormatter.format(f),
          type: (customField[f] && customField[f].type) ? customField[f].type : this._getFieldFormat(model[f]),
          validators: (customField[f] && customField[f].validators) ? customField[f].validators : {},
          hint: (customField[f] && customField[f].hint)? customField[f].hint : '',
        };

        if(customField[f] && customField[f].options){
          form[f].options = customField[f].options;
        }
        if(customField[f] && customField[f].properties){
          form[f].properties = customField[f].properties;
        }
        if(form[f].type === 'date'){
          model[f] = new Date(model[f]);
        }

        if(form[f].type === 'number'){
          model[f] = parseInt(model[f], 10);
        }

        return form;
      }, {});
    };

    /**
    * @ngdoc method
    * @name xos.uiComponents.XosFormHelpers#parseModelField
    * @methodOf xos.uiComponents.XosFormHelpers
    * @description
    * Helpers for buildFormStructure, convert a list of model properties in an object used to build the form structure, eg:
    * ```
    * // input:
    * ['id', 'name'm 'mail']
    *
    * // output
    * {
    *   id: {},
    *   name: {},
    *   mail: {}
    * }
    * ```
    * @param {array} fields An array of fields representing the model properties
    * @returns {object} An object containing one property for each field of the model
    **/

    this.parseModelField = (fields) => {
      return _.reduce(fields, (form, f) => {
        form[f] = {};
        return form;
      }, {});
    }

  });
})();