(function() {
  'use strict';

  /**
   * @ngdoc service
   * @name xos.uiComponents.Comparato
   * @description This factory define a function that replace the native angular.filter comparator. It is done to allow the comparation between (0|1) values with booleans.
   **/

  angular
    .module('xos.uiComponents')
    .factory('Comparator', comparator);

  function comparator() {

    return function(actual, expected){
      if (angular.isUndefined(actual)) {
        // No substring matching against `undefined`
        return false;
      }
      if ((actual === null) || (expected === null)) {
        // No substring matching against `null`; only match against `null`
        return actual === expected;
      }
      if (angular.isObject(expected) || (angular.isObject(actual))){
        return angular.equals(expected, actual);
      }

      if(_.isBoolean(actual) || _.isBoolean(expected)){
        if(actual === 0 || actual === 1){
          actual = !!actual;
        }
        return angular.equals(expected, actual);
      }

      if(!angular.isString(actual) || !angular.isString(expected)){
        if(angular.isDefined(actual.toString) && angular.isDefined(expected.toString)){
          actual = actual.toString();
          expected = expected.toString();
        }
        else {
          return actual === expected;
        }
      }

      actual = actual.toLowerCase() + '';
      expected = expected.toLowerCase() + '';
      return actual.indexOf(expected) !== -1;
    };
  }
})();
