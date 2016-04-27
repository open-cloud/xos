(function() {
  'use strict';

  /**
  * @ngdoc service
  * @name xos.helpers.NoHyperlinks
  * @description This factory is automatically loaded trough xos.helpers and will add an $http interceptor that will add ?no_hyperlinks=1 to your api request, that is required by django
  **/

  angular
      .module('xos.helpers')
      .factory('NoHyperlinks', noHyperlinks);

  function noHyperlinks() {
    return {
      request: function(request){
        if(request.url.indexOf('.html') === -1){
          request.url += '?no_hyperlinks=1';
        }
        return request;
      }
    };
  }
})();