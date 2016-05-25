(function() {
  'use strict';

  /**
  * @ngdoc service
  * @name xos.uiComponents.LabelFormatter
  * @description This factory define a set of helper function to format label started from an object property
  **/

  angular
      .module('xos.uiComponents')
      .factory('LabelFormatter', labelFormatter);

  function labelFormatter() {

    const _formatByUnderscore = string => string.split('_').join(' ').trim();

    const _formatByUppercase = string => string.split(/(?=[A-Z])/).map(w => w.toLowerCase()).join(' ');

    const _capitalize = string => string.slice(0, 1).toUpperCase() + string.slice(1);

    const format = (string) => {
      string = _formatByUnderscore(string);
      string = _formatByUppercase(string);

      string = _capitalize(string).replace(/\s\s+/g, ' ') + ':';
      return string.replace('::', ':');
    };

    return {
      // test export
      _formatByUnderscore: _formatByUnderscore,
      _formatByUppercase: _formatByUppercase,
      _capitalize: _capitalize,
      // export to use
      format: format
    };
  }
})();
