(function() {
    'use strict';

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