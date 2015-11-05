(function() {
    'use strict';

    angular
        .module('xos.helpers')
        .factory('SetCSRFToken', setCSRFToken);

    function setCSRFToken($cookies) { 
      return {
        request: function(request){
          if(request.method !== 'GET'){
            request.headers['X-CSRFToken'] = $cookies.get('xoscsrftoken');
          }
          return request;
        }
      };
    }
})();